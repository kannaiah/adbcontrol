# ADB Control

View and control Android device which is connected via ADB. As long as device is connected through adb touch events, button presses are sent to device and the updated sceen is displayed.
### Prerequisities
- ADB client
- Python 2.7 and PyQt4

## Install
```
git clone https://github.com/kannaiah/adbcontrol.git
```
## Usage
Maximize the widnow.
ip address of the device can be provided using the settings menu and press connect button.
```
python splitview.py
```
Or before launching the application, connect to device through adb and make sure there is only one device connected to adb.

```
adb connect <ip address>
```
# Demonstration
[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/JavS94AiGVM/0.jpg)](http://www.youtube.com/watch?v=JavS94AiGVM)

# Issues
- Only single device is supported.
- Not all buttons work.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments
* The icons are downloaded from https://icons8.com/
* I developed this to control Android apps installed on my Amazon firestick for which there was no remote support.
