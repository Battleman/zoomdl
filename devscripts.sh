#!/bin/bash
PYTHON="/usr/bin/env python3"
LOCALBIN="/usr/local/bin/"
EXEC="zoomdl"
EXEC_FOLDER="build"
ZIP_FOLDER="zip"
SRC_FOLDER="zoomdl"

compile(){
	mkdir -p $EXEC_FOLDER  # create folder for executable
	mkdir -p $ZIP_FOLDER  #create folder to zip
	cp -r $SRC_FOLDER $ZIP_FOLDER  #copy all python files
	mv $ZIP_FOLDER/$SRC_FOLDER/__main__.py $ZIP_FOLDER  #put main above src
	pip3 install -r requirements.txt --target $ZIP_FOLDER
	rm -r $ZIP_FOLDER/*.dist-info
	python3 -m zipapp -p "$PYTHON" -c -o $EXEC_FOLDER/$EXEC $ZIP_FOLDER
	rm -rf $ZIP_FOLDER
}

build(){
	compile
}

install(){
	compile
	sudo cp $EXEC_FOLDER/$EXEC $LOCALBIN
}

if [[ $# -ne 1 ]]
then
	echo "Usage: $0 'command'"
	echo "Valid commands: 'build', 'compile', 'install'"
	exit 1
else
	"$@"
fi
