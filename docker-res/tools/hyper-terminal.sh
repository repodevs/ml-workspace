#!/bin/sh

# Stops script execution if a command has an error
set -e

INSTALL_ONLY=0
# Loop through arguments and process them: https://pretzelhands.com/posts/command-line-flags
for arg in "$@"; do
    case $arg in
        -i|--install) INSTALL_ONLY=1 ; shift ;;
        *) break ;;
    esac
done

if [ ! -f "/opt/Hyper/hyper" ]; then
    echo "Installing Hyper Terminal"
    cd $RESOURCES_PATH
    apt-get update
    apt-get -f install
    wget --quiet https://releases.hyper.is/download/deb -O ./hyper.deb
    dpkg -i ./hyper.deb
    rm ./hyper.deb
else
    echo "Hyper Terminal is already installed"
fi

# Run
if [ $INSTALL_ONLY = 0 ] ; then
    echo "Starting Hyper Terminal"
    /opt/Hyper/hyper
    sleep 10
fi
