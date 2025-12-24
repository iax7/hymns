#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NUM=${1:-100}
echo "Generating $NUM hymn images..."

for i in $(seq 1 $NUM); do
  python3 "$SCRIPT_DIR/generate_image.py" "$i"
done

echo "✓ All images generated in static/images/"
