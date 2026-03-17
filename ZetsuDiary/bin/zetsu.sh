#!/bin/sh
# Zetsu Diary - KUAL Extension Launcher
# This script launches the Python diary application and refreshes
# the Kindle E-ink display when the app exits.

APP_DIR="/mnt/us/extensions/ZetsuDiary/bin"

# Launch the diary application using Python 3.
# Redirect all output (stdout + stderr) to a crash log so any Python error
# is captured and readable from the Kindle document library.
python3 "$APP_DIR/app.py" > /mnt/us/documents/Zetsu_Crash_Log.txt 2>&1

# Refresh the E-ink screen after the application closes
eips -f -g
