#!/bin/bash
set -e

PROJECT_DIR="$HOME/itp_sniper_gui"
cd "$PROJECT_DIR"

rm -rf build dist itp_sniper_gui.spec
python3 -m PyInstaller --noconfirm --onedir --windowed itp_sniper_gui.py

echo "Build complete. Output directory: $PROJECT_DIR/dist"

# 可选生成 DMG
if command -v hdiutil >/dev/null 2>&1; then
  hdiutil create -volname itp_sniper_gui -srcfolder "$PROJECT_DIR/dist" -ov -format UDZO "$PROJECT_DIR/itp_sniper_gui.dmg"
  echo "DMG generated: $PROJECT_DIR/itp_sniper_gui.dmg"
else
  echo "hdiutil not found, skip DMG packaging"
fi
