#!/bin/bash
# Symlink cgw into ~/.local/bin so edits in this repo take effect immediately.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/bin"
ln -sfn "$DIR/cgw" "$HOME/.local/bin/cgw"
echo "linked ~/.local/bin/cgw -> $DIR/cgw"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "add ~/.local/bin to PATH";; esac
