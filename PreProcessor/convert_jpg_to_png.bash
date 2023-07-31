#!/bin/bash

# Get a list of all JPG files in the current directory
jpg_files=$(find $1 -type f -name "*.jpg")

# Convert each JPG file to a PNG file
for jpg_file in $jpg_files; do
    png_file=$(echo $jpg_file | sed 's/.jpg/.png/')
    convert $jpg_file $png_file
done

# Remove the JPG files
rm $jpg_files

