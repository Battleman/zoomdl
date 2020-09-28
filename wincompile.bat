pyinstaller --onefile -n zoomdl zoom_dl\__main__.py
move /Y dist\zoomdl.exe .
rmdir /S /Q dist build
del zoomdl.spec
