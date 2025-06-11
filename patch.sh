#!/bin/bash

# Default values
clean=false
lang="en"
ks="trueToastedCode-release-key.jks"
ks_key_alias="trueToastedCode-key"
ks_pass="pass:StrongPass123!"

# Parse command line arguments
for arg in "$@"; do
    if [ "$arg" = "-clean" ]; then
        clean=true        
    elif [[ "$arg" == -lang* ]]; then
        lang="${arg#-lang}"
    elif [[ "$arg" == -ks=* ]]; then
        ks="${arg#-ks=}"
    elif [[ "$arg" == -ks_key_alias=* ]]; then
        ks_key_alias="${arg#-ks_key_alias=}"
    elif [[ "$arg" == -ks_pass=* ]]; then
        ks_pass="${arg#-ks_pass=}"
    fi
done

assets_dir="assets"
build_dir="build"

# compile elf_add_needed if neccessary
if [ ! -f "elf_add_needed" ]; then
    gcc -o "elf_add_needed" "elf_add_needed.c"
fi

# generate default keystore if neccessary
if [ "$ks" = "trueToastedCode-release-key.jks" ] && \
    [ ! -f "trueToastedCode-release-key.jks" ]; then
    ./generate_keystore.sh
fi

# prepare build dir
if [ "$clean" = true ]; then
    rm -rf "$build_dir"
fi
mkdir -p "${build_dir}/extract" "${build_dir}/apks"

# patch com.ninebot.segway
if [ ! -d "${build_dir}/extract/com.ninebot.segway" ]; then
    rm -rf "${build_dir}/apks/com.ninebot.segway_signed.apk"
    apktool d -s "${assets_dir}/apks/com.ninebot.segway.apk" -o "${build_dir}/extract/com.ninebot.segway"
    ./modify_manifest.py "${build_dir}/extract/com.ninebot.segway/AndroidManifest.xml"
    apktool b "${build_dir}/extract/com.ninebot.segway" -o "${build_dir}/apks/com.ninebot.segway.apk"
fi

# patch config.arm64_v8a
if [ ! -d "${build_dir}/extract/config.arm64_v8a" ]; then
    rm -rf "${build_dir}/apks/config.arm64_v8a_signed.apk"
    apktool d -s -r "${assets_dir}/apks/config.arm64_v8a.apk" -o "${build_dir}/extract/config.arm64_v8a"
    cp "${assets_dir}/libnbdrift.so" "${build_dir}/extract/config.arm64_v8a/lib/arm64-v8a/lipc.so"
    ./elf_add_needed "${build_dir}/extract/config.arm64_v8a/lib/arm64-v8a/libnesec.so" "libc.so" "lipc.so"
    apktool b "${build_dir}/extract/config.arm64_v8a" -o "${build_dir}/apks/config.arm64_v8a.apk"
fi

# sign apks
apks_to_sign=(
    "com.ninebot.segway.apk"
    "config.arm64_v8a.apk"
    "config.${lang}.apk"
    "config.xxhdpi.apk"
)

for apk in "${apks_to_sign[@]}"; do
    declare src_apk

    if [ -f "${build_dir}/apks/$apk" ]; then
        src_apk="${build_dir}/apks/$apk"
    elif [ -f "${assets_dir}/apks/$apk" ]; then
        src_apk="${assets_dir}/apks/$apk"
    else
        echo "Error: '$apk' not found." >&2
        exit 1
    fi

    if [ ! -f "${build_dir}/apks/${apk%.apk}_signed.apk" ]; then
        apksigner \
            sign \
            --verbose \
            --ks \
            "$ks" \
            --ks-key-alias \
            "$ks_key_alias" \
            --ks-pass \
            "$ks_pass" \
            --out \
            "${build_dir}/apks/${apk%.apk}_signed.apk" \
            "$src_apk"
    fi
done
