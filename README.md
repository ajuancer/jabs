# JABS
A new way to backup your android phone (via wireless) to your pc!

## What is?
[MTP](https://en.wikipedia.org/wiki/Media_Transfer_Protocol) is the tool provided by Windows to manage your phone files -or so their creators pretend-. After several frustrating attempts to use it, I decided to come to a different solution. I wrote a python script as a  secure and suitable way to transfer my files. By now it is only functional for phones using Android because [ADB](https://developer.android.com/studio/command-line/adb), the Android Debug Bridge, is the system I connected my devices through. Thus, it also works for Windows, Mac and Linux. Any other systems will depend on ADB disponibility -or on any similar tool-.

## Downloads
You can fork, clone or just download the .zip of this project. Go to your git bash and type `git clone https://github.com/ajuancer/jabs`

## Installation.
1. Get the necessary libraries with `pip install requeriments.txt`.
2. Run the [`main.py`](main.py) file. If you need help, try with `py main.py -h`.

## I want to help!
Although no documentation is written, you can fork this project and made the changes you want. You can also open an issue suggesting any kind of implementation. If you have any problem, you can always [contact me](https://ajuancer.github.io).

## I'm facing some problems.
Start by opening an issue [here](https://github.com/ajuancer/jabs/issues)

## License
Under GNU Affero v3. [See details](./LICENSE_aclarations.md).
