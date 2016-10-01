from PyQt4 import QtCore, QtGui
from icons import *
import base64
import logging
import sys, os
import subprocess
import tempfile
import time

logger = logging.getLogger('Fire')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)


def execute_command(command, lcwd=None):
    w = tempfile.NamedTemporaryFile(delete=False)
    lines = None
    retcode = None
    try:
        res = subprocess.Popen(command, shell=True, stdout=w, stderr=w, bufsize=0,
                               cwd=lcwd)
        res.wait()
    except OSError as e:
        logger.error("OSError > %s", e.errno)
        logger.error("OSError > %s", e.strerror)
        logger.error("OSError > %s", e.filename)
    except:
        logger.error("Error > %s", sys.exc_info()[0])

        if res.returncode != 0:
            logger.error( 'adb cannot be found specify correct path' )

        else:
            logger.info( 'adb found!')

    retcode = res.returncode
    with open(w.name, 'r') as r:
        lines = r.readlines()
    w.close()
    return (retcode, lines)

# execute_command(['dir'])
##########################################################################
class ADB():
    adb_path = None
    def __init__(self, padb=None):
        #' Check if adb is present'
        if padb:
            # pathh provided
            ADB.adb_path = padb
        else:
            # adb is in pathh
            ADB.adb_path = 'adb'
        # Check if adb is working
        res = execute_command([ADB.adb_path, 'help'])
        self.devs = None

    def getDevice(self, num=0):
        if len(self.devs) > 0:
            return self.devs[0]
        else:
            None

    def connect(self, ipaddr, port=''):
        lport = ':'+ port if port != '' else ''
        self.call("connect " + ipaddr + lport)
        self.devs = self.devices()

    def call(self, command, name = ''):
        command_result = ''
        dev_str = ''
        if name != '':
            dev_str = ' -s ' + name

        command_text = ADB.adb_path + dev_str + ' %s' % command
        logger.info( 'Command: %s', command_text )
        results = os.popen(command_text, "r")
        while 1:
            line = results.readline()
            if not line: break
            command_result += line
        return command_result

    def devices(self):
        result = self.call("devices")
        devices = result.partition('\n')[2].replace('\n', '').split('\tdevice')
        return [device for device in devices if len(device) > 2]

    def get(self, fr, to, name = ''):
        result = self.call("pull " + fr + " " + to, name)
        return result

    def screenshot(self, output, name = ''):
        self.call("shell screencap -p /sdcard/temp_screen.png", name)
        self.get("/sdcard/temp_screen.png", output, name)
        self.call("shell rm /sdcard/temp_screen.png", name)

    def touchAt(self, x, y, name=''):
        # Send touch event on screen
        self.call("shell input touchscreen tap %d %d" % (x,y))

##########################################################################
class Device(ADB):
    def __init__(self, name):
        self.dev_name = name

    def screenshot(self, output):
        ADB.screenshot(self, output, self.dev_name)

##########################################################################
mapActionCommand = {"UP":"input keyevent 19", "DOWN":"input keyevent 20", "LEFT":"input keyevent 21",
                    "RIGHT":"input keyevent 22", "ENTER":"input keyevent 66", "BACK":"input keyevent 4",
                    "HOME":"input keyevent 3", "MENU":"input keyevent 1",
                    "POTRAIT":"content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1",
                    "LANDSCAPE":"content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:0",
                    "AUTOROTATEOFF":"content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:0",
                    "AUTOROTATEON":"content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:0"}
##########################################################################
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setUI(self)
        self.adb_path = None
        self.ipAddress = None
        self.uiAdb = ADB()
        self.imageScaleFactor = 1.0
        self.labelInited = None
        self.screenx = None
        self.screeny = None

    def creatIconFromBase64(self, data):
        icon = QtGui.QIcon()
        pm = QtGui.QPixmap()
        pm.loadFromData(base64.b64decode(data))
        icon.addPixmap(pm, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        return icon

    def setIconFromBase64(self, icon, data):
        pm = QtGui.QPixmap()
        pm.loadFromData(base64.b64decode(data))
        icon.addPixmap(pm, QtGui.QIcon.Normal, QtGui.QIcon.Off)

    def addButtonWithIcon(self, buttonName="", data_b64=None, btn_txt=""):
        btn = QtGui.QPushButton()
        btn.setText(_fromUtf8(btn_txt))
        if data_b64 is not None:
            icon = self.creatIconFromBase64(data_b64)
            btn.setIcon(icon)
            btn.setIconSize(QtCore.QSize(32, 32))
        btn.resize(btn.sizeHint())
        btn.setObjectName(_fromUtf8(buttonName))
        return btn

    def resizeEvent(self,resizeEvent):
        self.updateDisplay()

    def setUI(self, MainWindow):
        self.image_widget = QtGui.QWidget()
        self.image_widget.setAutoFillBackground(True)
        p = self.image_widget.palette()
        p.setColor(self.image_widget.backgroundRole(), QtCore.Qt.darkGray)
        self.image_widget.setPalette(p)

        btnwidget = QtGui.QWidget()
        vLayout = QtGui.QVBoxLayout(btnwidget)
        hLayout = QtGui.QHBoxLayout()
        btn_layout = QtGui.QGridLayout()
        btn_layout.setMargin(0)
        hLayout.addStretch(1)
        hLayout.addLayout(btn_layout)
        hLayout.addStretch(1)
        vLayout.addStretch(1)
        vLayout.addLayout(hLayout)
        vLayout.addStretch(1)

        self.pushButtonLeft  = self.addButtonWithIcon("pushButtonLeft", left_b64)
        self.pushButtonRight = self.addButtonWithIcon("pushButtonRight", right_b64)
        self.pushButtonConnect =  self.addButtonWithIcon("pushButtonConnect",disconnected_b64)
        self.pushButtonUpdate = self.addButtonWithIcon("pushButtonUpdate", sync_b64)
        self.pushButtonMenu = self.addButtonWithIcon("pushButtonMenu", menu_b64)
        self.pushButtonBack = self.addButtonWithIcon("pushButtonBack",return_b64)
        self.pushButtonHome = self.addButtonWithIcon("pushButtonHome", home_b64)
        self.pushButtonPotrait = self.addButtonWithIcon( "pushButtonPotrait",potrait_b64)
        self.pushButtonLandscape = self.addButtonWithIcon("pushButtonLandscape", landscape_b64)
        self.pushButtonAutorotate = self.addButtonWithIcon("pushButtonAutorotate", autorotate_b64)
        self.pushButtonUp = self.addButtonWithIcon("pushButtonUp", up_b64)
        self.pushButtonDown = self.addButtonWithIcon("pushButtonDown", down_b64)
        self.pushButtonNoAutorotate = self.addButtonWithIcon("pushButtonNoAutorotate", no_auto_b64)

        btn_layout.addWidget(self.pushButtonUpdate, 0,0)
        btn_layout.addWidget(self.pushButtonRight, 5,2)
        btn_layout.addWidget(self.pushButtonConnect, 0,2)
        btn_layout.addWidget(self.pushButtonLeft, 5,0)
        btn_layout.addWidget(self.pushButtonMenu, 3,0)
        btn_layout.addWidget(self.pushButtonHome, 3,1)
        btn_layout.addWidget(self.pushButtonBack, 3,2)
        btn_layout.addWidget(self.pushButtonUp, 4,1)
        btn_layout.addWidget(self.pushButtonDown, 6,1)
        btn_layout.addWidget(self.pushButtonPotrait, 1,0)
        btn_layout.addWidget(self.pushButtonAutorotate, 1,1)
        btn_layout.addWidget(self.pushButtonLandscape, 1,2)
        btn_layout.addWidget(self.pushButtonNoAutorotate, 2,1)

        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.image_widget)
        self.splitter.addWidget(btnwidget)
        self.setCentralWidget(self.splitter)
        self.image_label = QtGui.QLabel(self.image_widget)
        self.image_label.setAlignment(QtCore.Qt.AlignLeft)
        self.image_label.setScaledContents(False)
        pixmap = QtGui.QPixmap(self.image_widget.geometry().width(), self.image_widget.geometry().height())
        pixmap.fill(QtCore.Qt.lightGray)
        self.image_label.setPixmap(pixmap)
        # Menubar
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName(_fromUtf8("menuSettings"))
        MainWindow.setMenuBar(self.menubar)
        self.actionSetIPAddress = QtGui.QAction(MainWindow)
        self.actionSetIPAddress.setObjectName(_fromUtf8("actionSetIPAddress"))
        self.actionSetADBPath = QtGui.QAction(MainWindow)
        self.actionSetADBPath.setObjectName(_fromUtf8("actionSetADBPath"))
        self.menuSettings.addAction(self.actionSetIPAddress)
        self.menuSettings.addAction(self.actionSetADBPath)
        self.menubar.addAction(self.menuSettings.menuAction())
        # Actions
        self.actionSetIPAddress.triggered.connect(self.acceptIPAddress)
        self.actionSetADBPath.triggered.connect(self.getADBPath)
        self.actionSetIPAddress.triggered.connect(self.acceptIPAddress)
        self.actionSetADBPath.triggered.connect(self.getADBPath)
        # Add button methods
        self.pushButtonUpdate.clicked.connect(self.updateScreenShot)
        self.pushButtonUp.clicked.connect(self.moveUp)
        self.pushButtonDown.clicked.connect(self.moveDown)
        self.pushButtonConnect.clicked.connect(self.ConnectToDevice)
        self.pushButtonLeft.clicked.connect(self.moveLeft)
        self.pushButtonRight.clicked.connect(self.moveRight)
        self.pushButtonMenu.clicked.connect(self.clickMenu)
        self.pushButtonHome.clicked.connect(self.clickHome)
        self.pushButtonBack.clicked.connect(self.clickBack)
        self.pushButtonPotrait.clicked.connect(self.potrait)
        self.pushButtonLandscape.clicked.connect(self.landscape)
        self.pushButtonAutorotate.clicked.connect(self.clickAutoRotate)
        self.pushButtonNoAutorotate.clicked.connect(self.clickNoAutoRotate)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings", None))
        self.actionSetIPAddress.setText(_translate("MainWindow", "ip address", None))
        self.actionSetADBPath.setText(_translate("MainWindow", "adb location", None))

    def acceptIPAddress(self):
       logger.info('Accept IP address')
       text, ok = QtGui.QInputDialog.getText(self, 'Enter IP address', 'xxx.xxx.xxx.xxx:yyyy')

       if ok:
           self.ipAddress = text
       logger.info( "IP address being used: %s", self.ipAddress)
       # Connect to device

    def getADBPath(self):
        logger.info('Locating ADB Path')
        self.adb_path = QtGui.QFileDialog.getOpenFileName(self, 'Locate ADB')
        logger.info( 'ADB Path: %s', self.adb_path )
        self.uiAdb = ADB(str(self.adb_path))
        # Initialiaze ADB.path
    def moveDown(self):
        logger.info( 'Button Move Down' )
        self.updateScreenShot()

    def moveUp(self):
        logger.info('Button Move Up')
        self.uiAdb.call("shell "+mapActionCommand['UP'])
        self.updateScreenShot()

    def moveRight(self):
        logger.info('Button Move Right' )
        self.uiAdb.call("shell "+mapActionCommand['RIGHT'])
        self.updateScreenShot()

    def moveLeft(self):
        logger.info( 'Button Move Left' )
        self.uiAdb.call("shell "+mapActionCommand['LEFT'])
        self.updateScreenShot()

    def clickMenu(self):
        logger.info('Button clickMenu ')
        self.uiAdb.call("shell "+mapActionCommand['MENU'])
        self.updateScreenShot()

    def clickHome(self):
        logger.info(' Button clickHome ')
        self.uiAdb.call("shell "+mapActionCommand['HOME'])
        self.updateScreenShot()

    def clickBack(self):
        logger.info(' Button clickBack ')
        self.uiAdb.call("shell "+mapActionCommand['BACK'])
        self.updateScreenShot()
        
    def clickAutoRotate(self):
        logger.info(' Button clickAutoRotate ')
        self.uiAdb.call("shell "+mapActionCommand['AUTOROTATEON'])
        self.updateScreenShot()

    def clickNoAutoRotate(self):
        logger.info(' Button clickNoAutoRotate ')
        self.uiAdb.call("shell "+mapActionCommand['AUTOROTATEOFF'])
        self.updateScreenShot()

    def potrait(self):
        logger.info(' Button potrait ')
        self.uiAdb.call("shell "+mapActionCommand['POTRAIT'])
        self.updateScreenShot()

    def landscape(self):
        logger.info(' Button landscape ')
        self.uiAdb.call("shell "+mapActionCommand['LANDSCAPE'])
        self.updateScreenShot()

    def ConnectToDevice(self):
        logger.info('ConnectToDevice')
        if not self.uiAdb:
            self.uiAdb = ADB()

        if ADB.adb_path and self.ipAddress:
            # All set connect to device
            logger.info( 'Connecting to device')
            self.uiAdb.connect(str(self.ipAddress))
            self.change_icon()
        else:
            # Warning to setup ip address and connect
            if not self.adb_path:
                msg = "adb path not set!"
            else:
                msg = "IP address not set"
            QtGui.QMessageBox.warning(self, "Warning!", msg, QtGui.QMessageBox.Ok)

    def change_icon(self):
        icon = self.creatIconFromBase64(connected_b64)
        self.pushButtonConnect.setIcon(icon)

    def updateScreenShot(self):
        # Get new screen shot
        logger.info('Update screnshot.png')
        time.sleep(1)
        self.uiAdb.screenshot('screenshot.png')
        self.updateDisplay()

    def updateDisplay(self):
        logger.info( 'Updating display image' )
        orig_pixmap = QtGui.QPixmap(_fromUtf8('screenshot.png'))
        scale0 = self.image_widget.geometry().height()*1.0/orig_pixmap.height()
        scale1 = self.image_widget.geometry().width()*1.0/orig_pixmap.width()
        self.imageScaleFactor = min(scale0, scale1)

        width = int(self.imageScaleFactor*orig_pixmap.width())
        height = int(self.imageScaleFactor*orig_pixmap.height())
        pixmap = orig_pixmap.scaled(width, height, QtCore.Qt.KeepAspectRatio)

        logger.info('    scaled pixmap size: %s, %s', pixmap.width(),pixmap.height())
        logger.info('    Orig size         : %s, %s', orig_pixmap.width(), orig_pixmap.height())
        self.image_label.resize(self.image_widget.geometry().width(), self.image_widget.geometry().height())
        self.image_label.setPixmap(pixmap)
        logger.info( self.image_widget.geometry())
        logger.info(self.image_label.geometry())
        # Now updae label size to match the image
        if self.labelInited is None:
            # first time set
            logger.info('    Change image_label size to: %s, %s', pixmap.width(), pixmap.height())
            self.image_label.setGeometry(QtCore.QRect(0, 0, pixmap.width(), pixmap.height()))
            self.labelInited = 'done'
        self.screenx = int(pixmap.width())
        self.screeny = int(pixmap.height())

        logger.info( '    image scalefactor: %s', self.imageScaleFactor )

    def mousePressEvent(self, QMouseEvent):
        logger.info( 'mousePressEvent: ' )
        pos = QMouseEvent.pos()
        central = self.image_widget
        relx = pos.x() - central.x()
        rely = pos.y() - central.y()
        logger.info( '    mouseclick relative: %s', relx)
        logger.info( '    mouseclick relative: %s', rely)
        if ( (int(relx) < self.screenx) and (int(rely) < self.screeny)):
            logger.info("    mouse event inside ")
            sx = (pos.x() - central.x())/self.imageScaleFactor
            sy = (pos.y() - central.y())/self.imageScaleFactor
            logger.info( '    Mouse event at: %s, %s', int(sx), int(sy))
            self.uiAdb.touchAt(int(sx), int(sy))
            self.updateScreenShot()
        else:
            logger.info("    mouse event outside ")

    @classmethod
    def mouseReleaseEvent(self, QMouseEvent):
        cursor =QtGui.QCursor()
        
def main():
    app = QtGui.QApplication(sys.argv)
    fireui = MainWindow()
    fireui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()