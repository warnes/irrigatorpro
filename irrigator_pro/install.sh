#!/bin/bash

#SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )
#if [ -z "$SCRIPTPATH" ]; then
SCRIPTPATH=$(pwd -P)
#fi

APPNAME=$(basename $SCRIPTPATH)

echo "SCRIPTPATH=${SCRIPTPATH}"
echo "APPNAME=${APPNAME}"

#export PATH=${PATH}:
export WORKON_HOME=${SCRIPTPATH}/VirtualEnvs

## Setup Virtual Environment
source $( which virtualenvwrapper.sh ) 
mkdir -p ${WORKON_HOME}
mkvirtualenv --clear $APPNAME


## Install required packages
pip install -r requirements.txt --allow-unverified django-admin-tools
easy_install -a readline
easy_install http://trac-hacks.org/svn/announcerplugin/trunk

( cd thirdparty/TracDjangoAuth; python setup.py install )
