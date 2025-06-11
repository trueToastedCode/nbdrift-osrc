FROM ubuntu:22.04

ARG ANDROID_TOOLS_VERSION
ARG BUILD_TOOLS_VERSION
ARG APKTOOL_VERSION

ENV DEBIAN_FRONTEND=noninteractive

# install basic tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    sudo \
    file \
    bash \
    vim \
    python3 \
    python3-pip \
    wget \
    build-essential \
    openjdk-21-jdk \
    zip \
    p7zip-full \
    && apt-get clean

# make env.sh
RUN echo "export PATH=\$PATH" >> /etc/profile.d/env.sh && chmod +x /etc/profile.d/env.sh

# install lief
RUN python3 -m pip --no-input --disable-pip-version-check --quiet install lief

# install apktool
RUN APKTOOL_DIR=/opt/apktool && \
    mkdir -p ${APKTOOL_DIR} && \
    if [ -z "$APKTOOL_VERSION" ]; then \
        LATEST_RELEASE=$(curl -s https://api.github.com/repos/iBotPeaches/Apktool/releases/latest | jq -r '.tag_name'); \
        APKTOOL_VERSION=${LATEST_RELEASE}; \
    fi && \
    # Remove 'v' prefix from version for filename
    VERSION_NO_V=${APKTOOL_VERSION#v} && \
    DOWNLOAD_URL="https://github.com/iBotPeaches/Apktool/releases/download/${APKTOOL_VERSION}/apktool_${VERSION_NO_V}.jar" && \
    wget ${DOWNLOAD_URL} -O ${APKTOOL_DIR}/apktool.jar && \
    # Create wrapper script to make it executable as a command
    echo '#!/bin/bash' > /usr/local/bin/apktool && \
    echo "java -jar ${APKTOOL_DIR}/apktool.jar \"\$@\"" >> /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool

# install Android SDK
RUN ANDROID_SDK_ROOT=/opt/android-sdk && \
    mkdir -p ${ANDROID_SDK_ROOT} && \
    cd ${ANDROID_SDK_ROOT} && \
    if [ -z "$ANDROID_TOOLS_VERSION" ]; then \
        TOOLS_URL=$(curl -s https://developer.android.com/studio | grep -o 'https://dl.google.com/android/repository/commandlinetools-linux-[0-9]*_latest.zip' | head -1); \
    else \
        TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_TOOLS_VERSION}_latest.zip"; \
    fi && \
    if [ -z "$TOOLS_URL" ]; then \
        echo "ERROR: Unable to find Android SDK command line tools URL." && \
        exit 1; \
    fi && \
    wget ${TOOLS_URL} -O tools.zip && \
    mkdir -p cmdline-tools && \
    unzip tools.zip -d cmdline-tools && \
    mv cmdline-tools/cmdline-tools cmdline-tools/latest && \
    sed -i "\$i export ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT}" /etc/profile.d/env.sh && \
    sed -i "\$ s|\\\$PATH|:\${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:\\\$PATH|" /etc/profile.d/env.sh && \
    rm tools.zip

# install Android SDK components
RUN . /etc/profile.d/env.sh && \
    yes | sdkmanager --sdk_root=${ANDROID_SDK_ROOT} --licenses && \
    if [ -z "$BUILD_TOOLS_VERSION" ]; then \
        AVAILABLE_BUILD_TOOLS_PACKAGES=$(sdkmanager --list | grep -o "build-tools;[0-9.]*" | grep -v "\-r" | sort -Vr) && \
        BUILD_TOOLS_PACKAGE=$(echo "$AVAILABLE_BUILD_TOOLS_PACKAGES" | head -n 1) && \
        BUILD_TOOLS_VERSION=$(echo "$BUILD_TOOLS_PACKAGE" | cut -d';' -f2); \
    else \
        BUILD_TOOLS_PACKAGE="build-tools;${BUILD_TOOLS_VERSION}"; \
    fi && \
    sdkmanager --sdk_root=${ANDROID_SDK_ROOT} \
        "$BUILD_TOOLS_PACKAGE" && \
    sed -i "\$ s|:\\\$PATH|:\${ANDROID_SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}:\\\$PATH|" /etc/profile.d/env.sh

# add vscode user
RUN useradd -m vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# copy entrypoint and set permission
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# set permission for ANDROID_SDK_ROOT
RUN . /etc/profile.d/env.sh && chmod -R a+w "${ANDROID_SDK_ROOT}"

# set user and workdir
USER vscode
WORKDIR /home/vscode

# set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
