#!/bin/bash
# Get the latest snapshot file URL for oracle consumption

REPO="KudzayiKing/aigi-index-engine"
BRANCH="main"

# Get the latest snapshot filename
LATEST_FILE=$(ls -t epochs/*.json | head -n 1)

if [ -z "$LATEST_FILE" ]; then
    echo "Error: No snapshot files found"
    exit 1
fi

# Generate the raw GitHub URL
RAW_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/${LATEST_FILE}"

echo "Latest snapshot: $(basename $LATEST_FILE)"
echo "Raw URL: $RAW_URL"
echo ""
echo "To fetch with curl:"
echo "curl -s $RAW_URL | jq ."
