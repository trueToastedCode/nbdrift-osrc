# nbdrift
A project to repurpose the Ninebot app, turning the Ninebot into a companion for extended functionality without any scooter protocol reverse engineering.
## Disclaimer
Use of this project may affect your device or app in ways not intended by the original manufacturer. It is your responsibility to ensure that any modifications or usage comply with local laws and regulations. Always verify for yourself that your actions are legal in your country or region.
## Necessary Assets
### Segway Mobility
Compatible 6.9.1<br>
[Download here](https://apkpure.com/segway-ninebot/com.ninebot.segway/download/6.9.1)
### nbdrift Injection Lib
[Download here](https://drive.google.com/file/d/1c7P5YQv2bbzXvKQaadS49lG_w2wWM74S/view?usp=sharing](https://drive.google.com/drive/folders/1lKpRhx2mWYWAiIoIEPyJkhB75iPiTszy?usp=sharing))
## How to patch
1. Open the project folder in [Visual Studio Code](https://code.visualstudio.com/)
2. Ensure the [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) is installed
3. Run `Dev Containers: Rebuild and Reopen in Container` from the command palette
4. Copy the following files from your .xapk into the `assets/apks` folder:
   - com.ninebot.segway.apk
   - config.arm64_v8a.apk
   - config.en.apk
   - config.xxhdpi.apk
6. Copy libnbdrift.so into the assets folder.
7. Run the patch script: `./patch.sh`
## Installation
1. Ensure you have [Command-line tools](https://developer.android.com/tools) installed.
2. Linux/MacOS users can simply execute the installation script. `./install.sh`.
3. On your device, activate `Permissions > Allow management of all files`

Notice, that these steps must be executed on the host system, not inside the dev container.
## Usage
In your internal shared storage (commonly `/storage/emulated/0`), make a new folder named `nbdrift`. This is were it tries to find custom configuration files.

Update checks are always spoofed and cannot be disabled.

### Viewing the Logs / Dumping API Communication
- Using logcat: `adb logcat -s "nbdrift"`
- With cleaning: `clear && adb logcat -c && adb logcat -s "nbdrift"`

### Iot fw update response Spoofing
Write a custom server payload into `fw-iot.json`. This is useful for injecting custom firmware into the Ninebot app or disabling forced updates.

Example response for no available udpate:
`{"code":1,"data":{"parts_version":[],"show_kart_tip":false,"special_version_status":false,"forced_status":false,"forced_content":"","sub_wnumber":"","source":1},"desc":"Successfully"}`
### Serial Spoofing
Write a custom serial number into `sn-spoof.txt`. This is useful when the scooter has been patched to ignore limits imposed by its serial number. However, without this patch, it might still not show you the newly available options.
