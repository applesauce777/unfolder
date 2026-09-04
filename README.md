# 📂 Unfolder

Extract nested archives — zip inside zip inside zip — in one shot.

![Version](https://img.shields.io/badge/version-3.1-blue.svg) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg)

## What it does

Unfolder recursively walks a folder, finds any archive files inside it, extracts them, and repeats until nothing archive-like is left. It's built for cases like Google Takeout exports, where compressed files are buried inside other compressed files several layers deep.

```
takeout.zip
├── Drive.zip
│   ├── documents.zip
│   └── photos.zip
│       ├── 2021.zip
│       └── 2022.zip
```

Point Unfolder at the top-level folder and it fully unpacks the whole tree — no manual re-extracting at each level.

## Format support

| Format | Extensions | Requires |
|---|---|---|
| ZIP | `.zip` | Built in |
| TAR | `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2` | Built in |
| GZIP | `.gz` | Built in |
| BZIP2 | `.bz2` | Built in |
| RAR | `.rar` | `rarfile` (optional) |
| 7-Zip | `.7z` | `py7zr` (optional) |

## Features

- Recursively extracts nested archives of any depth, in rounds, until no new archives are found
- **Nested mode** (default): extracts each archive in place, preserving folder hierarchy
- **Flat mode** (`--flat`): extracts everything as siblings instead
- **Dry-run/preview** (`--dry-run`): see what would be extracted without touching anything
- Archives are only deleted (`--delete`) after *all* extraction rounds finish successfully, so an interrupted run can't lose data
- Failed or partial extractions are automatically cleaned up
- On Windows, detects if long-path support is disabled and offers to hand off to a native PowerShell/7-Zip fallback
- Works from the command line, or through a desktop GUI (browse to a folder, click Extract — no terminal needed)

## Install & run

### Option 1: Desktop app (no command line)

Clone or download the repo, then run the installer for your OS. Each one sets up a double-clickable app with a folder-browse dialog.

**Windows**
```powershell
git clone https://github.com/applesauce777/unfolder.git
cd unfolder
powershell -ExecutionPolicy Bypass -File install_windows.ps1
```
Creates a desktop shortcut. Add `-InstallOptionalFormats` to also enable RAR/7Z.

**macOS**
```bash
git clone https://github.com/applesauce777/unfolder.git
cd unfolder
chmod +x install_macos.sh
./install_macos.sh
```
Installs `Unfolder.app` to `~/Applications`. Add `--with-optional-formats` for RAR/7Z.

**Linux**
```bash
git clone https://github.com/applesauce777/unfolder.git
cd unfolder
chmod +x install_linux.sh
./install_linux.sh
```
Adds Unfolder to your application menu and Desktop. Requires `python3-tk` (or your distro's tkinter package) if not already installed. Add `--with-optional-formats` for RAR/7Z.

After installing, the cloned repo folder can be deleted if you want — the installed app is a self-contained copy. Keeping it around just makes future updates a simple `git pull` + re-run of the installer.

### Option 2: Command line (any OS)

Requires Python 3.7+.

```bash
git clone https://github.com/applesauce777/unfolder.git
cd unfolder

# Interactive — prompts for a folder
python unfolder.py

# Direct
python unfolder.py /path/to/archives

# Preview only, no extraction
python unfolder.py /path/to/archives --dry-run

# Extract and delete originals afterward
python unfolder.py /path/to/archives --delete

# Extract everything as siblings instead of nested
python unfolder.py /path/to/archives --flat
```

Full options:
```
python unfolder.py [folder] [options]

  folder          Path to scan (optional — prompts if omitted)
  --delete, -d    Delete archives after all extraction completes
  --no-delete     Keep archives after extraction (default)
  --dry-run       Preview without extracting (alias: --preview)
  --nested        Extract in place, preserving hierarchy (default; alias: --hierarchy)
  --flat          Extract everything as siblings
  --help, -h      Show help
  --version, -v   Show version
```

### Windows native option (no Python)

If you'd rather not use Python at all, `unzipper.ps1` does the same job using 7-Zip directly:
```powershell
.\unzipper.ps1
```
Requires [7-Zip](https://www.7-zip.org/) installed.

### Optional dependencies (RAR / 7Z)

```bash
pip install -r requirements.txt
```
Or manually: `pip install py7zr rarfile`. Without these, ZIP/TAR/GZ/BZ2 still work fully.

## Requirements

- Python 3.7+ (for the Python/GUI versions)
- ~10MB free disk space, 512MB RAM minimum
- Windows 7+, macOS 10.12+, or a modern Linux distro

## Privacy

Fully offline. No network access, no telemetry — files are processed locally and never leave your machine.

## License

MIT — see [LICENSE](LICENSE). Free to use, modify, and distribute, including commercially.

---

If Unfolder saved you some time, a [Ko-fi tip](https://ko-fi.com/applesauce777) is always appreciated but never expected.
