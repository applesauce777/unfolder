# 📂 Unfolder

**Stop the zip-in-zip nightmare. Extract nested archives with one command.**

![Version](https://img.shields.io/badge/version-3.1-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20This%20Project-ff5e5b?logo=ko-fi)](https://ko-fi.com/applesauce777)

---

## ✨ What is Unfolder?

**Before Unfolder:**
1. Extract archive A
2. Find archive B inside  
3. Extract archive B
4. Find archive C inside
5. Repeat forever... 😫

**With Unfolder:**
1. Run one command
2. Select folder (or specify path)
3. Done! ✅

Unfolder automatically extracts nested archives of any depth. Got a ZIP inside a ZIP inside a ZIP? Unfolder handles it all automatically.

**Perfect for**:
- Google Takeout exports
- Nested backup archives  
- Bulk data downloads
- Any "zip hell" situation

---

## 📦 Complete Format Support

| Format | Extension | Support Type |
|--------|-----------|--------------|
| ZIP | `.zip` | ✅ Built-in (no deps) |
| TAR | `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2` | ✅ Built-in (no deps) |
| RAR | `.rar` | ✅ Optional (rarfile) |
| 7-Zip | `.7z` | ✅ Optional (py7zr) |
| GZIP | `.gz` | ✅ Built-in (no deps) |
| BZIP2 | `.bz2` | ✅ Built-in (no deps) |

---

## 🚀 Quick Start

### 🐍 Python Version (Recommended)
```bash
# Interactive mode (with GUI folder selection when available):
python unfolder.py

# Direct mode (perfect for scripting):
python unfolder.py /path/to/archives

# Preview what will be extracted:
python unfolder.py /path/to/archives --dry-run

# With deletion (archives deleted AFTER all extraction completes):
python unfolder.py /path/to/archives --delete

# Flat extraction (extract all as siblings):
python unfolder.py /path/to/archives --flat
```

### 🪟 Windows Native Option
```powershell
# For Windows users who prefer native 7-Zip:
.\unzipper.ps1
```
**Requires**: 7-Zip installed (free download from 7-zip.org)

**NEW**: Python version will automatically offer to use PowerShell script if Windows long paths are disabled!

---

## ⌨️ Command Line Options

```bash
python unfolder.py [folder] [options]

Arguments:
  folder          Path to archive folder (optional - will ask if not provided)

Options:
  --delete, -d    Delete archives after successful extraction (at end)
  --no-delete     Keep archives after extraction (default)
  --dry-run       Preview what will be extracted without extracting
  --preview       Same as --dry-run
  --nested        Extract nested archives in-place - maintains hierarchy (default)
  --hierarchy     Same as --nested
  --flat          Extract all archives as siblings (alternative mode)
  --help, -h      Show this help message
  --version, -v   Show version information
```

---

## 🆕 What's New in Version 3.1

### 🛡️ Safer Deletion
- Archives are now deleted **only after ALL extraction rounds complete**
- Prevents data loss if the process is interrupted
- Clear status reporting of what was deleted

### 🧹 Smart Cleanup
- Failed extractions are automatically cleaned up
- Partial files removed if extraction fails
- No more mysterious half-extracted folders

### 👀 Dry-Run Mode
- Preview what will be extracted before running
- See file sizes, paths, and structure
- Perfect for large operations: `--dry-run`

### 🪟 Windows Long Path Intelligence
- Automatically detects Windows long path status
- Offers PowerShell fallback if long paths disabled
- Clear instructions for enabling long path support
- Seamless integration between Python and PowerShell versions

### 📁 Flexible Extraction Modes
- **Nested mode** (default): Maintain archive hierarchy, extract in-place
- **Flat mode** (`--flat`): Extract all archives as siblings
- Choose the structure that works for your use case

---

## 📦 Optional Dependencies

For full format support (RAR, 7Z), install optional dependencies:

```bash
pip install py7zr rarfile
```

**Or install from requirements file:**
```bash
pip install -r requirements.txt
```

**Without these, Unfolder still works perfectly with ZIP, TAR, GZ, and BZ2 formats.**

---

## 🛠️ Installation

### Method 1: Download & Run
1. Download the Unfolder package
2. Extract to any folder
3. Run: `python unfolder.py`

### Method 2: Clone Repository
```bash
git clone https://github.com/your-repo/unfolder.git
cd unfolder
python unfolder.py
```

### Method 3: Optional Dependencies
```bash
pip install -r requirements.txt
```
**Note**: Unfolder works perfectly with just ZIP/TAR formats without additional packages.

---

## ⚡ Performance

- **Speed**: Processes ~50MB/s on modern hardware
- **Memory**: Uses minimal RAM (streaming extraction)
- **Scalability**: Handles thousands of nested archives
- **Long Paths**: Smart Windows long path detection and fallback
- **Cross-Platform**: Optimized for Windows, macOS, and Linux

---

## 💡 Use Cases

### Google Takeout
```
takeout.zip
├── Drive.zip
│   ├── documents.zip
│   └── photos.zip
│       ├── 2021.zip
│       └── 2022.zip
```
**Unfolder extracts everything automatically**

### Data Migration
- Extract complex backup structures
- Maintain folder organization
- Clean up original archives safely

### Research & Analysis
- Process downloaded datasets
- Handle nested compressed files
- Preview before extracting with `--dry-run`

### System Administration
- Automated backup extraction
- Log archive processing
- Batch data processing with error recovery

---

## 🔒 Privacy & Security

- **100% Offline**: No internet connection required
- **Local Processing**: Your files never leave your computer
- **No Telemetry**: We don't track or collect data
- **Simple Code**: Full transparency in implementation
- **Open Source**: Review the code yourself

---

## 📋 System Requirements

### Minimum
- **Python 3.7+** (most systems have this)
- **Memory**: 512MB RAM
- **Storage**: 10MB free space
- **OS**: Windows 7+, macOS 10.12+, or modern Linux

### Recommended
- **Memory**: 2GB+ RAM
- **Storage**: 50MB+ free space
- **Processor**: Any modern CPU
- **Optional**: 7-Zip (for Windows PowerShell version)

---

## 🎁 Bonus Features

- **Smart Extraction**: Handles unlimited nesting depth
- **Format Detection**: Automatically identifies archive types
- **Error Recovery**: Skips corrupted files, continues extraction
- **Automatic Cleanup**: Removes partial extractions on failure
- **Progress Tracking**: See exactly what's being extracted
- **Performance Stats**: Speed, timing, and size reporting
- **Safe Deletion**: Delete archives only after ALL extraction completes
- **Dry-Run Preview**: See what will happen before running
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Long Path Support**: Smart detection and PowerShell fallback
- **GUI Fallback**: Uses system dialogs when available
- **Flexible Modes**: Nested (default) or flat extraction structures

---

## ❓ Common Questions

**Q: Does this require an internet connection?**
A: No! Unfolder runs 100% offline. Your files never leave your computer.

**Q: What's the difference from free tools like 7-Zip?**
A: 7-Zip requires you to manually extract each nested archive. Unfolder does it all automatically with one command.

**Q: Will this work on my Mac/Linux?**
A: Yes! Unfolder works on Windows, macOS, and Linux. We even include a native Windows PowerShell version.

**Q: Do I need to install anything?**
A: Just Python 3.7+. Optional libraries (py7zr, rarfile) add RAR/7Z support but aren't required.

**Q: How fast is it?**
A: Approximately 50MB/s on modern hardware, with real-time progress reporting and performance statistics.

**Q: Can it handle thousands of files?**
A: Yes! Unfolder is designed for scalability and can process thousands of nested archives efficiently.

**Q: What if an archive is corrupted?**
A: Unfolder skips corrupted files, cleans up partial extractions, and continues processing the rest.

**Q: What about Windows long path issues?**
A: Unfolder detects long path status and offers to use the PowerShell/7-Zip version if needed. You can also enable long paths system-wide (instructions provided).

**Q: When are archives deleted?**
A: Only AFTER all extraction rounds complete successfully. This prevents data loss if interrupted.

**Q: Can I preview before extracting?**
A: Yes! Use `--dry-run` to see exactly what will be extracted without actually extracting anything.

---

## ☕ Support This Project

If Unfolder saved you from zip-in-zip hell, consider buying me a coffee!

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20This%20Project-ff5e5b?logo=ko-fi&style=for-the-badge)](https://ko-fi.com/applesauce777)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**What this means:**
- ✅ **Free to use** for personal and commercial purposes
- ✅ **Free to modify** and adapt to your needs
- ✅ **Free to distribute** with your projects
- ✅ **No warranty** - use at your own risk
- ✅ **Open source** - review and contribute to the code

Perfect for both personal projects and commercial applications.

---

## 📝 Changelog

### Version 3.1 (Current)
- ✨ Added dry-run/preview mode
- 🛡️ Archives now deleted only after ALL extraction completes (safer)
- 🧹 Automatic cleanup of failed extractions
- 🪟 Smart Windows long path detection with PowerShell fallback
- 📁 Added nested vs flat extraction modes
- 📊 Improved statistics and error reporting
- 🎯 Better command-line argument handling

### Version 3.0
- Initial public release
- Support for ZIP, RAR, 7Z, TAR, GZ, BZ2
- Recursive extraction
- Optional deletion
- Cross-platform support

---

**📂 Unfolder - Finally, nested archives made simple.**

*Stop wrestling with nested archives. Start unfolding your files with one command.*
