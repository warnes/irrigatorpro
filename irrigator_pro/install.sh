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
pip install Werkzeug

# ## Link admin/static directory
# export DJANGO_PATH=$( find $VIRTUAL_ENV -name "django")
# mkdir -p static_extra
# ln -s ${DJANGO_PATH}/contrib/admin/static/admin static/admin
