#!/bin/bash
# Unfolder - macOS Installer
# Run as: chmod +x install_macos.sh && ./install_macos.sh
#
# Builds a real Unfolder.app bundle in ~/Applications so the end user
# can double-click it like any other Mac app - no Terminal required.

set -e

INSTALL_DIR="$HOME/Applications/Unfolder"
APP_DIR="$HOME/Applications/Unfolder.app"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}===============================================${NC}"
echo -e "${CYAN} Unfolder - macOS Installer${NC}"
echo -e "${CYAN}===============================================${NC}"
echo ""

# [1/5] Check Python 3
echo -e "${YELLOW}[1/5] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}  ERROR: python3 not found. Install it from python.org or 'brew install python3'.${NC}"
    exit 1
fi
PY_VERSION=$(python3 --version)
echo -e "${GREEN}  Found: $PY_VERSION${NC}"

# Check tkinter (bundled with python.org installers, sometimes missing from Homebrew python)
if ! python3 -c "import tkinter" &> /dev/null; then
    echo -e "${YELLOW}  WARNING: tkinter not found. The GUI needs it.${NC}"
    echo -e "${YELLOW}  If you installed Python via Homebrew, run: brew install python-tk${NC}"
fi

# [2/5] Create install directory and copy files
echo -e "${YELLOW}[2/5] Copying Unfolder files...${NC}"
mkdir -p "$INSTALL_DIR"
for file in unfolder.py unfolder_gui.py requirements.txt; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        cp "$SOURCE_DIR/$file" "$INSTALL_DIR/"
        echo -e "${GREEN}  Copied: $file${NC}"
    else
        echo -e "${YELLOW}  Skipped (not found next to installer): $file${NC}"
    fi
done

# Optional icon (icons/Unfolder.icns)
ICON_SOURCE="$SOURCE_DIR/icons/Unfolder.icns"
HAVE_ICON=false
if [ -f "$ICON_SOURCE" ]; then
    HAVE_ICON=true
    echo -e "${GREEN}  Found icon: Unfolder.icns${NC}"
fi

# [3/5] Optional dependencies (RAR / 7Z support)
echo -e "${YELLOW}[3/5] Optional format support...${NC}"
if [ "$1" == "--with-optional-formats" ]; then
    python3 -m pip install --quiet py7zr rarfile || \
        echo -e "${YELLOW}  Could not install optional packages - ZIP/TAR/GZ/BZ2 still work fine.${NC}"
    echo -e "${GREEN}  Installed py7zr + rarfile (RAR/7Z support enabled)${NC}"
else
    echo -e "  Skipped (re-run with --with-optional-formats to add RAR/7Z support)"
fi

# [4/5] Build the .app bundle
echo -e "${YELLOW}[4/5] Building Unfolder.app...${NC}"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

if [ "$HAVE_ICON" = true ]; then
    cp "$ICON_SOURCE" "$APP_DIR/Contents/Resources/Unfolder.icns"
fi

cat > "$APP_DIR/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Unfolder</string>
    <key>CFBundleDisplayName</key>
    <string>Unfolder</string>
    <key>CFBundleIdentifier</key>
    <string>com.applesauce777.unfolder</string>
    <key>CFBundleVersion</key>
    <string>3.1</string>
    <key>CFBundleExecutable</key>
    <string>Unfolder</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>Unfolder.icns</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

cat > "$APP_DIR/Contents/MacOS/Unfolder" << LAUNCHER
#!/bin/bash
cd "$INSTALL_DIR"
exec python3 unfolder_gui.py
LAUNCHER

chmod +x "$APP_DIR/Contents/MacOS/Unfolder"
echo -e "${GREEN}  Built: $APP_DIR${NC}"

# [5/5] Clear macOS's "unidentified developer" quarantine flag on our own bundle
echo -e "${YELLOW}[5/5] Finalizing...${NC}"
xattr -dr com.apple.quarantine "$APP_DIR" 2>/dev/null || true
echo -e "${GREEN}  Done${NC}"

echo ""
echo -e "${CYAN}===============================================${NC}"
echo -e "${GREEN} Installation Complete!${NC}"
echo -e "${CYAN}===============================================${NC}"
echo ""
echo -e "${YELLOW}Open 'Unfolder' from ~/Applications, or Launchpad/Spotlight.${NC}"
echo -e "${YELLOW}No Terminal needed - just browse to a folder and click Extract.${NC}"
echo ""
