# RPi-IDS
### 1. Download ids peak in [this website](https://en.ids-imaging.com/download-details/1008483.html?os=linux_arm&version=v8&bus=64&floatcalc=hard)
- camera model : U3-36L0XC Starter-Set
- operating system : Linux ARM v8 64-bit hard
- package download: Software > IDS peak 2.3 for Linux ARMv8 (64bit) - archive file
```
tar -xvzf ids-peak-linux-arm64-2.3.0.0.tgz -C ~/ids
```
### 2. Check system requirements
- Dependences:
```
sudo apt-get install libqt5core5a libqt5gui5 libqt5widgets5 libqt5quick5 qml-module-qtquick-window2 qml-module-qtquick2 qml-module-qtquick-dialogs qml-module-qtquick-controls qml-module-qtquick-layouts libusb-1.0-0 libqt5multimedia5
```
- recommends
```
sudo apt-get install cmake gtk2-engines-pixbuf qtbase5-dev qtdeclarative5-dev
```
### 3. Set environment variable
- Edit bashrc
```
cd ~
ls -a
nano .bashrc
```
- set environment variable
```
export GENICAM_GENTL64_PATH=$GENICAM_GENTL64_PATH:/home/peakvision/ids/ids-peak_2.3.0.0-15823_arm64/lib/ids/cti
```
- save the edit
```
source .bashrc
```
### 4. Double check the `Pyside` installation
```
sudo apt-get install python3-pyside2.qt3dcore python3-pyside2.qt3dinput python3-pyside2.qt3dlogic python3-pyside2.qt3drender python3-pyside2.qtcharts python3-pyside2.qtconcurrent python3-pyside2.qtcore python3-pyside2.qtgui python3-pyside2.qthelp python3-pyside2.qtlocation python3-pyside2.qtmultimedia python3-pyside2.qtmultimediawidgets python3-pyside2.qtnetwork python3-pyside2.qtopengl python3-pyside2.qtpositioning python3-pyside2.qtprintsupport python3-pyside2.qtqml python3-pyside2.qtquick python3-pyside2.qtquickwidgets python3-pyside2.qtscript python3-pyside2.qtscripttools python3-pyside2.qtsensors python3-pyside2.qtsql python3-pyside2.qtsvg python3-pyside2.qttest python3-pyside2.qttexttospeech python3-pyside2.qtuitools python3-pyside2.qtwebchannel python3-pyside2.qtwebsockets python3-pyside2.qtwidgets python3-pyside2.qtx11extras python3-pyside2.qtxml python3-pyside2.qtxmlpatterns
```
### 5. Installation of Python bindings
- Check Python version
```
python --version
```
My Python version is 3.9.2
- Go to directory `/home/peakvision/ids/ids-peak_2.3.0.0-15823_arm64/local/share/ids/bindings/python/wheel`
```
pip install ids_peak-1.5.0.0-cp39-cp39-linux_aarch64.whl
```
```
pip install ids_peak_ipl-1.6.0.0-cp39-cp39-linux_aarch64.whl
```
### 6. Increase Buffer size by edit `usbfs_memory_mb` variable
```
cd /sys/module/usbcore/parameters/
sudo chmod 777 usbfs_memory_mb
vi usbfs_memory_mb
```
Edit the value to 1000
press `i` to edit
`dd`to delete the whole line
Press'Esc' and type `:wq` to save the edit

### 7. Open the Camera
```
cd /home/peakvision/ids/ids-peak_2.3.0.0-15823_arm64/bin
sudo bash ids_peak_cockpit
```


