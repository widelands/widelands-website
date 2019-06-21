#!/bin/sh
# Updates all packages on the server, but stops the widelands website before
# doing so, in case mysql gets updated - it always results in really ugly
# errors for users otherwise.
#
# This script requires sudo.

set -ex

if [ -z "${TMUX}" ]; then 
   echo "Run inside screen or tmux in case SSH gets updated."
   exit 1
fi

sudo apt update

sudo systemctl stop wl-website
sudo systemctl start wl-bauarbeiten

sudo apt dist-upgrade

sudo systemctl stop wl-bauarbeiten
sudo systemctl start wl-website

sudo apt autoremove -y
