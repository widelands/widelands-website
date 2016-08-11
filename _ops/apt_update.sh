#!/bin/sh
# Updates all packages on the server, but stops the widelands website before
# doing so, in case mysql gets updated - it always results in really ugly
# errors for users otherwise. Ideally, this script would switch the website to
# a "In Maintenance" banner.
#
# This script requires root access.

set -ex

apt-get update
stop wlwebsite

apt-get dist-upgrade

start wlwebsite

apt-get autoremove -y
