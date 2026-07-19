#!/bin/bash

# Test it with a "Dry Run"
# `./deploy.sh -n`

# ==================== SERVER CONFIGURATION ====================
USER="xxx"                        # Replace with your server's User name
SERVER="192.168.x.x"              # Replace with your server's IP or domain
TARGET_DIR="/xxx/xxx/xxxx/xxxx"   # Parent directory where apps live on Ubuntu
# ==============================================================

# Ensure the ignore file exists
IGNORE_FILE=".rsync-ignore"
if [ ! -f "$IGNORE_FILE" ]; then
    echo "⚠️ Warning: $IGNORE_FILE not found. Deploying without exclusions."
    RSYNC_ARGS=(-avzP --delete --stats)
else
    RSYNC_ARGS=(-avzP --delete --stats --exclude-from="$IGNORE_FILE")
fi

# Capture any extra flags passed (e.g., -n)
EXTRA_FLAGS=("$@")

# Track if this is a dry run
IS_DRY_RUN=false
if [[ " ${EXTRA_FLAGS[*]} " =~ " -n " || " ${EXTRA_FLAGS[*]} " =~ " --dry-run " ]]; then
    IS_DRY_RUN=true
fi

RSYNC_SUCCESS=false

for SRC_PATH in "./backend" "./web"; do
    FOLDER_NAME=$(basename "$SRC_PATH")
    RSYNC_LOG="/tmp/rsync_deploy_${FOLDER_NAME}.log"

    if [ "$IS_DRY_RUN" = true ]; then
        echo "🔍 PERFORMING DRY RUN for '$FOLDER_NAME' (No files will be modified, Docker will not restart) ..."
    else
        echo "🚀 Mirroring local '$SRC_PATH' to remote '$TARGET_DIR/$FOLDER_NAME' ..."
    fi

    echo ""
    rsync "${RSYNC_ARGS[@]}" "${EXTRA_FLAGS[@]}" "$SRC_PATH/" "$USER@$SERVER:$TARGET_DIR/$FOLDER_NAME/" | tee "$RSYNC_LOG"
    echo ""

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        FILES_CHANGED=$(grep -i "transferred" "$RSYNC_LOG" | grep -o '[0-9]\+' | head -n 1)
        FILES_DELETED=$(grep -i "deleted" "$RSYNC_LOG" | grep -o '[0-9]\+' | head -n 1)

        if [ -z "$FILES_CHANGED" ]; then FILES_CHANGED=0; fi
        if [ -z "$FILES_DELETED" ]; then FILES_DELETED=0; fi

        TOTAL_CHANGES=$((FILES_CHANGED + FILES_DELETED))

        rm -f "$RSYNC_LOG"

        if [ "$IS_DRY_RUN" = false ]; then
            if [ "$TOTAL_CHANGES" -gt 0 ]; then
                RSYNC_SUCCESS=true
            fi
        fi
    else
        echo "❌ Error: Deployment failed during rsync phase for '$FOLDER_NAME'. Aborting Docker rebuild."
        rm -f "$RSYNC_LOG"
        exit 1
    fi
done

if [ "$RSYNC_SUCCESS" = true ]; then
    echo "Detected change(s). Builing services ..."
    echo "----------------------------------------------------------------------------"
    echo ""
    echo "1. Stopping services ..."
    echo ""
    ssh "$USER@$SERVER" "cd '$TARGET_DIR' && docker compose down -v"
    echo ""
    echo "2. Starting services ..."
    echo ""
    ssh "$USER@$SERVER" "cd '$TARGET_DIR' && docker compose up -d --build"
    echo "----------------------------------------------------------------------------"
    echo ""
    echo "Deployed changes to server."
else
    echo "No file modifications is detected."
fi
