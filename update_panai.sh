#!/bin/bash

# 🧠 update_panai.sh
# A helper script to safely update and restart the PanAI Seed Node service on a local machine.
# This script is designed to be run from any node in a PanAI cluster.
# It attempts to gracefully pull the latest Git changes and restart the service,
# offering options if local changes would cause a conflict.

# Stop the service before updating
echo "🧠 Stopping panai service..."
sudo systemctl stop panai

# Define fallback paths to search for the panai-seed-node repo
PATHS=(
  "$HOME/george/services/panai-seed-node"
  "$HOME/services/panai-seed-node"
)

# Try each known repo path
for DIR in "${PATHS[@]}"; do
  if [ -d "$DIR" ]; then
    cd "$DIR" || exit 1
    echo "📥 Attempting to pull latest changes from $DIR..."

    # Perform a dry-run pull to detect potential conflicts
    GIT_OUTPUT=$(git pull --dry-run 2>&1)
    if echo "$GIT_OUTPUT" | grep -q "Already up to date."; then
      echo "✅ Repository already up to date."
      echo "🚀 Restarting panai service..."
      sudo systemctl start panai
      echo "✅ Done. Use 'journalctl -u panai -f' to follow logs."
      exit 0
    fi

    if echo "$GIT_OUTPUT" | grep -q "would be overwritten by merge"; then
      echo "⚠️ Git pull would overwrite local changes. Choose an action:"
      echo "1) Restore and Pull (discard local changes)"
      echo "2) Stash and Pull (preserve changes)"
      echo "3) Abort"

      read -rp "Select option (1/2/3): " CHOICE

      case "$CHOICE" in
        1)
          echo "♻️ Restoring repo to match remote..."
          git reset --hard HEAD
          git pull
          ;;
        2)
          echo "📦 Stashing local changes..."
          git stash
          git pull
          git stash pop
          ;;
        3)
          echo "❌ Aborting update."
          exit 1
          ;;
        *)
          echo "❌ Invalid choice. Aborting."
          exit 1
          ;;
      esac
    else
      echo "📥 Pulling latest changes..."
      git pull
    fi

    echo "🚀 Restarting panai service..."
    sudo systemctl start panai
    echo "✅ Done. Use 'journalctl -u panai -f' to follow logs."
    exit 0
  fi
done

echo "❌ Could not find panai-seed-node directory in expected locations."
exit 1