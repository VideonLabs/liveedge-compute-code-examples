#!/bin/bash

# Helpfully borrowed from: https://www.baeldung.com/linux/monitor-changes-directory-tree

PROCESSING="false"

file_removed() {
    TIMESTAMP=`date`
    echo "[$TIMESTAMP]: $2 was removed from $1"
}

file_modified() {
    TIMESTAMP=`date`
    echo "[$TIMESTAMP]: The file $1$2 was modified"
}

file_created() {
    TIMESTAMP=`date`
    echo "[$TIMESTAMP]: The file $1$2 was created"
}

file_closed() {
    TIMESTAMP=`date`
    echo "[$TIMESTAMP]: The file $1$2 was closed"

    if [ $PROCESSING == "false" ]
    then
        if [ "$2" != "" ]
        then
            echo "Syncing to cloud..."
            PROCESSING="true"
            `rclone sync $1 videon-aws-s3:${SYNC_BUCKET}`
            echo "Sync complete."
            PROCESSING="false"
        fi
    fi
}

echo "Monitoring $1..."

inotifywait -q -m -r -e modify,delete,create,close_write $1 | while read DIRECTORY EVENT FILE; do
    case $EVENT in
        MODIFY*)
            file_modified "$DIRECTORY" "$FILE"
            ;;
        CREATE*)
            file_created "$DIRECTORY" "$FILE"
            ;;
        DELETE*)
            file_removed "$DIRECTORY" "$FILE"
            ;;
        CLOSE*)
            file_closed "$DIRECTORY" "$FILE"
            ;;
    esac
done