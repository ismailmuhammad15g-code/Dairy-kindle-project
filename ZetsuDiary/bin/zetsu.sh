#!/bin/sh
# Zetsu Diary - KUAL Extension Launcher
# This script launches the Python diary application and refreshes
# the Kindle E-ink display when the app exits.

APP_DIR="/mnt/us/extensions/ZetsuDiary/bin"

# Launch the diary application using Python 3
python3 "$APP_DIR/app.py"

# Refresh the E-ink screen after the application closes
eips -f -g
