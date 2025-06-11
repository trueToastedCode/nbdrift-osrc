# nbdrift
A project to repurpose the Ninebot app, turning the Ninebot itself into a companion for extended functionality.
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
4. Copy the following files from your .xapk into the assets/apks folder:
   - com.ninebot.segway.apk
   - config.arm64_v8a.apk
   - config.en.apk
   - config.xxhdpi.apk
6. Copy libnbdrift.so into the assets folder.
7. Run the patch script: `./patch.sh`
## Installation
1. Ensure you have [Command-line tools](https://developer.android.com/tools) installed.
2. Linux/MacOS users can simply execute the installation script. `./install.sh`.

Notice, that these steps must be executed on the host system, not inside the dev container.
