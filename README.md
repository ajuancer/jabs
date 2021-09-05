# JABS
A new way to backup your android phone (via wireless) to your pc!

## What is?
[MTP](https://en.wikipedia.org/wiki/Media_Transfer_Protocol) is the tool provided by Windows to manage your phone files -or so their creators pretend-. After several frustrating attempts to use it, I decided to come to a different solution. I wrote a python script as a  secure and suitable way to transfer my files. By now it is only functional for phones using Android because [ADB](https://developer.android.com/studio/command-line/adb), the Android Debug Bridge, is the system I connected my devices through. Thus, it also works for Windows, Mac and Linux. Any other systems will depend on ADB availability -or on any similar tool-.

## Downloads
You can fork, clone or just download the .zip of this project. Go to your git bash and type `git clone https://github.com/ajuancer/jabs`.

## Set up.

#### 1. Get the Android Debug Bridge.

As this script uses the ADB, you will need to download it from the [official Android site](https://developer.android.com/studio/releases/platform-tools). If you are an android developer and you have the Android SDK Platform-Tools package, ADB is by default located in the `platform-tools` dir (you can download or update this package through the [SDK manager](https://developer.android.com/studio/intro/update#sdk-manager)).

You can visit the [official documentation](https://developer.android.com/studio/command-line/adb) for more info.

#### 2. Prepare your phone.

1. Navigate to the directory where the ADB you have just downloaded is located (the folder with the `adb.exe` file).
2. Open a terminal in that directory.
3. Connect the phone to your computer with a USB cable.
4. Say to your phone "please, listen to a TCP/IP connection on this port!" with `adb tcpip 5555`.
5. Disconnect the USB from your phone.
6. Now run `adb kill-server` to ensure no conflicts while connecting to the phone. You can now close the terminal.

Check the [android documentation](https://developer.android.com/studio/command-line/adb#wireless) for more info about this tool. 

_Note 1:_ Please note that the android guide performs some final different steps because the goal is different.

_Note 2_: If your Android version is 11 or higher, you can follow different steps as stated in the [documentation](https://developer.android.com/studio/command-line/adb#connect-to-a-device-over-wi-fi-android-11+).

#### 3. Get the paths.

Now you just need to specify some parameters:

1. The IP of your phone. Usually it is detailed in the Wifi settings. It follows the following pattern: `192.168.x.jj`, where the `x` is commonly a `0` and `jj` a two-digit number.
2. The path to where the ADB key you generated in [step #2](#2-prepare-your-phone) is located. This file works just like in a lock, allowing the computer to connect to your phone. Please keep it private.
3. The path to the root dir of your backup folder (where you want your files to be saved). For example, if you want to save them is an external drive `E:`, on the folder `android_backup`, your backup path is `E:/android_backup`.
4. The path of the folder you want to backup. This is the folder of the android device. You need to specify the absolute path, so it should start with a slash (**`/`**`some/path/`). You can get this path using any file explorer of your device. A common path to the camera folder is `/storage/emulated/0/DCIM/Camera/`.

## Run the script.

1. Get the necessary libraries with `pip install requeriments.txt`.
2. Run the [`main.py`](main.py) file. If you need help, try with `py main.py -h`.

_Help:_ If you have followed the [previous step](#3-get-the-paths), you just need to open a console in the directory where the `main.py` file is and write `py main.py phone_IP ADB_key backup_folder phone_folder`, but replacing `phone_IP` with what you obtained in step 3.1, `ADB_key` with 3.2, `backup_folder` with 3.3 and `phone_folder` with 3.4.

## I want to help!
Although no documentation is written, you can fork this project and made the changes you want. You can also open an issue suggesting any kind of implementation. If you have any problem, you can always [contact me](https://ajuancer.github.io).

## I'm facing some problems.
Start by opening an issue [here](https://github.com/ajuancer/jabs/issues).

## License.
Under GNU Affero v3. [See details](./LICENSE_aclarations.md).
