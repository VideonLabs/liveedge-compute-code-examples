#!/bin/bash
# Wrapper for ffmpeg commands to actually concatenate .ts files
# from the LiveEdge circular buffer and produce the clip
# 

if [ $# -ne 3 ]; then
    echo "Usage: $0 <file_output> <start_time> <stop_time>"
    exit 1
fi

if ! [ -d /recordings ]; then
   echo "LiveEdge recordings not accessible. Abort."
   exit 1
fi

cd /recordings
VID="VID" # basename for "Filename" in the File Record settings

output_file="$1"

if [ -f "$output_file" ]; then
    echo "Destination file "$1" exists, skipping."
    exit 0
fi

# Remove human-readable date formats
start_time=$(echo "$2" | sed -n 's/_//p')
stop_time=$(echo "$3" | sed -n 's/_//p')

function calculate_offset() {
    if [ $# -ne 2 ]; then
        return 1
    fi

    start_date=$1
    stop_date=$2

    # Check the operating system to determine the date command syntax
    if [[ $(uname) == "Darwin" ]]; then
        start_timestamp=$(date -jf "%Y%m%d%H%M%S" "$start_date" "+%s" 2>/dev/null)
        stop_timestamp=$(date -jf "%Y%m%d%H%M%S" "$stop_date" "+%s" 2>/dev/null)
    else
	start_date="${start_date:0:8} ${start_date:8:2}:${start_date:10:2}:${start_date:12:2}"
	stop_date="${stop_date:0:8} ${stop_date:8:2}:${stop_date:10:2}:${stop_date:12:2}"
        start_timestamp=$(date -d "$start_date" +"%s" 2>/dev/null)
        stop_timestamp=$(date -d "$stop_date" +"%s" 2>/dev/null)
    fi

    if [ -z "$start_timestamp" ] || [ -z "$stop_timestamp" ]; then
        echo "Error: Invalid date format or unsupported date command."
        return 1
    fi

    # Calculate the offset in seconds
    if [[ "$stop_timestamp" -ge "$start_timestamp" ]]; then
	    offset=$((stop_timestamp - start_timestamp))
    else
	    offset=$((start_timestamp - stop_timestamp))
    fi

    echo $offset
}

##########
# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed. Please install ffmpeg first."
    exit 1
fi

###########
# Find the appropriate video files based on the provided start and stop times
video_files=($(ls -1 "$VID"_*.ts | sort))
filtered_video_files=()

previous_file=""
for file in "${video_files[@]}"; do
    # Extract the timestamp from the filename
    file_start_time=$(echo "$file" | sed -n 's/'"$VID"'_\([0-9_]*\)\.ts/\1/p' | sed -n 's/_//p')
    if [ "$file_start_time" -ge "$start_time" ]; then
        if [ ${#filtered_video_files[@]} -eq 0 ]; then
           filtered_video_files+=("$previous_file") # if first video added
           filtered_video_files+=("$file")
        elif [ "$file_start_time" -le "$stop_time" ]; then
           filtered_video_files+=("$file") # don't add if past the stop_time
        fi
    fi
    previous_file="$file"
done

if [ ${#filtered_video_files[@]} -eq 0 ]; then
    echo "No video files found within the specified time range."
    exit 1
fi

# Initialize a temporary list file to store the selected video files
tmp_list_file=./tmp_list.txt
for file in "${filtered_video_files[@]}"; do
    echo "file '$file'" >> "$tmp_list_file"
done

echo "List of files:"
cat "$tmp_list_file"

# Concatenate the selected video files within the time range
ffmpeg -f concat -safe 0 -i "$tmp_list_file" -c copy TMP_"$output_file"_concatenated.ts

# Calculate the time offset for the start and stop times
begin_time=$(cat "$tmp_list_file" | head -n 1 | sed -n 's/.*'"$VID"'_\([0-9_]*\)\.ts.*/\1/p' | sed -n 's/_//p')
end_time=$(cat "$tmp_list_file" | tail -n 1 | sed -n 's/.*'"$VID"'_\([0-9_]*\)\.ts.*/\1/p' | sed -n 's/_//p')
start_offset=$(calculate_offset "$start_time" "$begin_time")
stop_offset=$(calculate_offset "$stop_time" "$start_time")
stop_offset=$((start_offset + stop_offset))

echo "Offets:"
echo " > start: $start_offset"
echo " > stop: $stop_offset"

# Trim the concatenated video to the specified start and stop times
ffmpeg -i TMP_"$output_file"_concatenated.ts -ss "$start_offset" -to "$stop_offset" -c copy "$output_file"

# Clean up temporary files
rm -f "$tmp_list_file" TMP_"$output_file"_concatenated.ts

echo "Clipped  video created as $output_file"
