#!/bin/bash
clear
SOURCE_FILE=~/Downloads/database_ntoo.db
DEST_FILE=~/code/ntoo_simple/database_ntoo.db

curl -L https://nottheonlyone.org/download_database -o "$SOURCE_FILE"

# Check file size in bytes (4MB = 4 * 1024 * 1024 = 4194304 bytes)
FILE_SIZE=$(stat -c '%s' "$SOURCE_FILE")

if (( FILE_SIZE > 4194304 )); then
  cp "$SOURCE_FILE" "$DEST_FILE"
  echo "File copied to $DEST_FILE"
  ls -alh "$SOURCE_FILE"
  md5sum "$SOURCE_FILE"
  md5sum "$DEST_FILE"
  sqlite3 "$DEST_FILE" "select count(*) from ntoo_item;"
  cd ~/code/ntoo_simple
  git status
  SOURCE_FILE=~/Downloads/database_ntoo.db
  DEST_FILE=~/code/ntoo_simple/database_ntoo.db

  cd ~/code/ntoo_simple
  git status
  git commit -a -m "Updating database as backup"
  git push
else
  echo "File size is less than or equal to 4MB. Skipping copy."
  ls -alh "$SOURCE_FILE"
fi


