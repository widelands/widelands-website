#!/bin/sh
# Updates all packages on the server, but stops the widelands website before
# doing so, in case mysql gets updated - it always results in really ugly
# errors for users otherwise. Ideally, this script would switch the website to
# a "In Maintenance" banner.
#
# This script requires root access.

set -ex

if [ -z "$STY" ] && [ -z "$TMUX" ]; then 
   echo "Run inside screen or tmux in case SSH gets updated."
   exit 1
fi

apt-get update
stop wlwebsite || true

# TODO(sirver): Upgrading widelands-data takes a long time (~30 minutes or
# longer). Use apt-mark hold to not update widelands and widelands-data to
# bring the website up quicker again. Then only upgrade those packages later,
# after the website is up again.
# See http://askubuntu.com/questions/99774/exclude-packages-from-apt-get-upgrade
apt-get dist-upgrade

start wlwebsite

apt-get autoremove -y
