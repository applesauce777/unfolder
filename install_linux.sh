#!/bin/bash
# Unfolder - Linux Installer
# Run as: chmod +x install_linux.sh && ./install_linux.sh
#
# Installs Unfolder to ~/.local/share/unfolder, registers it as a desktop
# app (shows up in your app menu / launcher), and drops a double-clickable
# icon on the Desktop too. No terminal needed after this.

set -e

INSTALL_DIR="$HOME/.local/share/unfolder"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="$HOME/Desktop"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}===============================================${NC}"
echo -e "${CYAN} Unfolder - Linux Installer${NC}"
echo -e "${CYAN}===============================================${NC}"
echo ""

# [1/6] Check Python 3 and tkinter
echo -e "${YELLOW}[1/6] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}  ERROR: python3 not found. Install it with your package manager, e.g.:${NC}"
    echo -e "${RED}    Debian/Ubuntu: sudo apt install python3${NC}"
    echo -e "${RED}    Fedora:        sudo dnf install python3${NC}"
    echo -e "${RED}    Arch:          sudo pacman -S python${NC}"
    exit 1
fi
PY_VERSION=$(python3 --version)
echo -e "${GREEN}  Found: $PY_VERSION${NC}"

if ! python3 -c "import tkinter" &> /dev/null; then
    echo -e "${YELLOW}  WARNING: tkinter not found. The GUI needs it. Install with:${NC}"
    echo -e "${YELLOW}    Debian/Ubuntu: sudo apt install python3-tk${NC}"
    echo -e "${YELLOW}    Fedora:        sudo dnf install python3-tkinter${NC}"
    echo -e "${YELLOW}    Arch:          sudo pacman -S tk${NC}"
fi

# [2/6] Create install directory and copy files
echo -e "${YELLOW}[2/6] Copying Unfolder files...${NC}"
mkdir -p "$INSTALL_DIR"
for file in unfolder.py unfolder_gui.py requirements.txt; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        cp "$SOURCE_DIR/$file" "$INSTALL_DIR/"
        echo -e "${GREEN}  Copied: $file${NC}"
    else
        echo -e "${YELLOW}  Skipped (not found next to installer): $file${NC}"
    fi
done

# Optional icon (icons/Unfolder.png - 256x256 recommended)
ICON_SOURCE="$SOURCE_DIR/icons/Unfolder.png"
HAVE_ICON=false
if [ -f "$ICON_SOURCE" ]; then
    mkdir -p "$ICON_DIR"
    cp "$ICON_SOURCE" "$ICON_DIR/unfolder.png"
    HAVE_ICON=true
    echo -e "${GREEN}  Installed icon: unfolder.png${NC}"
fi

# [3/6] Optional dependencies (RAR / 7Z support)
echo -e "${YELLOW}[3/6] Optional format support...${NC}"
if [ "$1" == "--with-optional-formats" ]; then
    python3 -m pip install --quiet --user py7zr rarfile || \
        echo -e "${YELLOW}  Could not install optional packages - ZIP/TAR/GZ/BZ2 still work fine.${NC}"
    echo -e "${GREEN}  Installed py7zr + rarfile (RAR/7Z support enabled)${NC}"
else
    echo -e "  Skipped (re-run with --with-optional-formats to add RAR/7Z support)"
fi

# [4/6] Create launcher script
echo -e "${YELLOW}[4/6] Creating launcher...${NC}"
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/unfolder-gui" << LAUNCHER
#!/bin/bash
cd "$INSTALL_DIR"
exec python3 unfolder_gui.py
LAUNCHER
chmod +x "$BIN_DIR/unfolder-gui"
echo -e "${GREEN}  Created: $BIN_DIR/unfolder-gui${NC}"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}  Note: $BIN_DIR is not on your PATH. Desktop/menu launches still work fine;${NC}"
    echo -e "${YELLOW}  this only matters if you want to type 'unfolder-gui' in a terminal.${NC}"
fi

# [5/6] Register as a desktop application (app menu entry)
echo -e "${YELLOW}[5/6] Registering desktop entry...${NC}"
mkdir -p "$APPS_DIR"
ICON_LINE="Icon=utilities-archive-manager"
if [ "$HAVE_ICON" = true ]; then
    ICON_LINE="Icon=unfolder"
fi

cat > "$APPS_DIR/unfolder.desktop" << DESKTOP
[Desktop Entry]
Type=Application
Name=Unfolder
Comment=Extract nested archives (zip inside zip inside zip)
Exec=$BIN_DIR/unfolder-gui
$ICON_LINE
Terminal=false
Categories=Utility;Archiving;
DESKTOP
chmod +x "$APPS_DIR/unfolder.desktop"
echo -e "${GREEN}  Registered in application menu${NC}"

# Refresh desktop database if available (no-op if not installed)
command -v update-desktop-database &> /dev/null && \
    update-desktop-database "$APPS_DIR" 2>/dev/null || true

# [6/6] Desktop shortcut
echo -e "${YELLOW}[6/6] Creating Desktop shortcut...${NC}"
if [ -d "$DESKTOP_DIR" ]; then
    cp "$APPS_DIR/unfolder.desktop" "$DESKTOP_DIR/Unfolder.desktop"
    chmod +x "$DESKTOP_DIR/Unfolder.desktop"
    # GNOME/Nautilus requires marking launchers as trusted before they're clickable
    command -v gio &> /dev/null && \
        gio set "$DESKTOP_DIR/Unfolder.desktop" metadata::trusted true 2>/dev/null || true
    echo -e "${GREEN}  Created: ~/Desktop/Unfolder.desktop${NC}"
else
    echo -e "  No ~/Desktop folder found - skipped (app menu entry still works)"
fi

echo ""
echo -e "${CYAN}===============================================${NC}"
echo -e "${GREEN} Installation Complete!${NC}"
echo -e "${CYAN}===============================================${NC}"
echo ""
echo -e "${YELLOW}Find 'Unfolder' in your application menu, or double-click${NC}"
echo -e "${YELLOW}the Desktop icon. No terminal needed after this.${NC}"
echo ""
echo -e "  (Some desktops show an 'Untrusted application launcher' prompt"
echo -e "   the first time you double-click a new .desktop file - choose"
echo -e "   'Trust and Launch' or 'Allow Launching' if asked.)"
echo ""
