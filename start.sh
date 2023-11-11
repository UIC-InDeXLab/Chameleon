#!/bin/bash

# List of project directories
project_directories=("Gateway" "ImageAnalyzer" "MaskGenerator" "ImageEditor" "UCB")

# Initialize the starting port number
port=8000

# Loop through the project directories
for project_dir in "${project_directories[@]}"; do
  # Check if the directory exists
  if [ -d "$project_dir" ]; then
    echo "Activating virtual environment for $project_dir..."
    
    source "$project_dir/venv/bin/activate"
    
    cd "$project_dir"
    
    uvicorn main:app --host 0.0.0.0 --port $port &
    
    port=$((port + 1))
    
    deactivate

    cd ..
  else
    echo "Project directory $project_dir does not exist."
  fi
done

cd UI/fairness-lens/
npm start & 

cd ../../
# Wait for all uvicorn processes to finish
wait

