# Google Photos Date Fix
Purpose: Add timestamp to photos and videos in Google Photos takeout

The project relies on exiftool from https://exiftool.org/

The code reads timestamp from the json files in Google Photos takeout and add it to the jpg and mp4 files, so that these files can show properly in the timeline of other album apps.

Usage:
1. Place jpg and mp4 files without timestamp in a source folder
2. Place json files in a separate folder
3. Designate a destination folder and run the script
