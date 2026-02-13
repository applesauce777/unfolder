#!/usr/bin/env python3
"""
Unfolder - Simple Cross-Platform Archive Extractor
Extracts nested archives (ZIP, RAR, 7Z, TAR, GZ, BZ2) recursively.
Pure Python standard library + optional py7zr/rarfile.

Version: 3.1
"""

import os
import sys
import zipfile
import tarfile
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Optional libraries for extended format support
try:
    import py7zr
    HAS_7Z = True
except ImportError:
    HAS_7Z = False

try:
    import rarfile
    HAS_RAR = True
except ImportError:
    HAS_RAR = False


def check_long_path_support_windows():
    """Check Windows long path status and provide guidance"""
    if sys.platform != 'win32':
        return True  # Not Windows, no issue
    
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, 
            r"SYSTEM\CurrentControlSet\Control\FileSystem", 
            0, winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
        winreg.CloseKey(key)
        
        if value == 1:
            print("✅ Windows long path support is enabled")
            return True
        else:
            print("⚠️  Windows long path support is DISABLED")
            print("   This may cause issues with deeply nested folders.")
            print()
            return False
    except:
        # Can't read registry (probably not admin), assume it might work
        print("ℹ️  Cannot check long path status (non-admin)")
        return None  # Unknown status


def offer_powershell_fallback():
    """Offer to use PowerShell script with 7-Zip for better long path support"""
    print()
    print("💡 ALTERNATIVE: Use PowerShell script with 7-Zip")
    print("   7-Zip handles long paths natively without system configuration.")
    print()
    
    # Check if unzipper.ps1 exists
    ps1_path = Path(__file__).parent / "unzipper.ps1"
    
    if not ps1_path.exists():
        print(f"   ❌ PowerShell script not found at: {ps1_path}")
        print("   Continuing with Python version...")
        return False
    
    print(f"   Found: {ps1_path}")
    print()
    response = input("   Use PowerShell script instead? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        try:
            # Launch PowerShell script
            print()
            print("🚀 Launching PowerShell script...")
            subprocess.run(['powershell.exe', '-ExecutionPolicy', 'Bypass', 
                          '-File', str(ps1_path)], check=True)
            return True
        except Exception as e:
            print(f"   ❌ Failed to launch PowerShell: {e}")
            print("   Continuing with Python version...")
            return False
    
    return False


class SimpleExtractor:
    def __init__(self, source_folder, delete_after=False, maintain_hierarchy=False):
        self.source_folder = Path(source_folder)
        self.delete_after = delete_after
        self.maintain_hierarchy = maintain_hierarchy
        self.processed_files = set()
        self.pending_deletions = []  # Track archives to delete at end
        self.stats = {
            'extracted': 0, 
            'failed': 0, 
            'deleted': 0,
            'total_size': 0,
            'cleaned_up': 0
        }
        self.start_time = None
        
    def _is_archive(self, file_path):
        """Check if file is a supported archive"""
        file_path_str = str(file_path).lower()
        archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.tgz', '.tar.gz', '.tar.bz2']
        return any(file_path_str.endswith(ext) for ext in archive_extensions)
    
    def _get_file_size(self, file_path):
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size
        except:
            return 0
    
    def _format_size(self, size_bytes):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def _extract_zip(self, archive_path, extract_to):
        """Extract ZIP files"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Check for password protection
                if zip_ref.testzip() is None and any(needs_pwd for needs_pwd in [f.flag_bits & 0x1 for f in zip_ref.infolist()]):
                    print(f"  ⚠️  ZIP may be password protected - will attempt extraction")
                
                # Get file count for progress
                file_count = len(zip_ref.infolist())
                if file_count > 100:
                    print(f"  📊 Extracting {file_count} files...")
                
                zip_ref.extractall(extract_to)
            return True
        except zipfile.BadZipFile:
            print(f"  ❌ ZIP file is corrupted or invalid")
            return False
        except PermissionError:
            print(f"  ❌ Permission denied - check file/folder permissions")
            return False
        except OSError as e:
            if "No space left" in str(e):
                print(f"  ❌ Disk full - not enough space to extract")
            elif "name too long" in str(e).lower():
                print(f"  ❌ Path too long - try PowerShell version on Windows")
            else:
                print(f"  ❌ System error: {e}")
            return False
        except Exception as e:
            print(f"  ❌ ZIP extraction failed: {e}")
            return False
    
    def _extract_rar(self, archive_path, extract_to):
        """Extract RAR files"""
        if not HAS_RAR:
            print(f"  ⚠️  Skipping RAR: rarfile not installed (pip install rarfile)")
            return False
        try:
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                # Check if RAR is password protected
                if rar_ref.needs_password():
                    print(f"  ⚠️  RAR is password protected - extraction may fail")
                
                # Get file count for progress
                try:
                    file_count = len(rar_ref.infolist())
                    if file_count > 50:
                        print(f"  📊 Extracting {file_count} files...")
                except:
                    pass  # Some RAR files don't support this
                
                rar_ref.extractall(extract_to)
            return True
        except rarfile.BadRarFile:
            print(f"  ❌ RAR file is corrupted or invalid")
            return False
        except rarfile.PasswordRequired:
            print(f"  ❌ RAR requires password - unsupported")
            return False
        except PermissionError:
            print(f"  ❌ Permission denied - check file/folder permissions")
            return False
        except Exception as e:
            print(f"  ❌ RAR extraction failed: {e}")
            return False
    
    def _extract_7z(self, archive_path, extract_to):
        """Extract 7Z files"""
        if not HAS_7Z:
            print(f"  ⚠️  Skipping 7Z: py7zr not installed (pip install py7zr)")
            return False
        try:
            with py7zr.SevenZipFile(archive_path, 'r') as seven_z_ref:
                # Check if 7Z is password protected
                if seven_z_ref.password_protected:
                    print(f"  ⚠️  7Z is password protected - extraction may fail")
                
                # Get file count for progress
                file_count = len(seven_z_ref.files)
                if file_count > 100:
                    print(f"  📊 Extracting {file_count} files...")
                
                seven_z_ref.extractall(extract_to)
            return True
        except py7zr.Bad7zFile:
            print(f"  ❌ 7Z file is corrupted or invalid")
            return False
        except py7zr.PasswordRequired:
            print(f"  ❌ 7Z requires password - unsupported")
            return False
        except PermissionError:
            print(f"  ❌ Permission denied - check file/folder permissions")
            return False
        except Exception as e:
            print(f"  ❌ 7Z extraction failed: {e}")
            return False
    
    def _extract_tar(self, archive_path, extract_to):
        """Extract TAR, TAR.GZ, TAR.BZ2, TGZ files"""
        try:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                # Get file count for progress
                file_count = len(tar_ref.getnames())
                if file_count > 50:
                    print(f"  📊 Extracting {file_count} files...")
                
                tar_ref.extractall(extract_to)
            return True
        except tarfile.ReadError:
            print(f"  ❌ TAR file is corrupted or invalid")
            return False
        except tarfile.CompressionError:
            print(f"  ❌ TAR compression error - file may be corrupted")
            return False
        except PermissionError:
            print(f"  ❌ Permission denied - check file/folder permissions")
            return False
        except OSError as e:
            if "No space left" in str(e):
                print(f"  ❌ Disk full - not enough space to extract")
            elif "name too long" in str(e).lower():
                print(f"  ❌ Path too long - try PowerShell version on Windows")
            else:
                print(f"  ❌ System error: {e}")
            return False
        except Exception as e:
            print(f"  ❌ TAR extraction failed: {e}")
            return False
    
    def _get_extract_method(self, file_path):
        """Get the appropriate extraction method"""
        file_path_str = str(file_path).lower()
        if file_path_str.endswith('.zip'):
            return self._extract_zip
        elif file_path_str.endswith('.rar'):
            return self._extract_rar
        elif file_path_str.endswith('.7z'):
            return self._extract_7z
        else:  # TAR, GZ, BZ2, TGZ, TAR.GZ, TAR.BZ2
            return self._extract_tar
    
    def _get_extraction_path(self, archive_path):
        """Determine where to extract the archive"""
        parent_dir = archive_path.parent
        base_name = archive_path.stem
        
        # Handle double extensions like .tar.gz
        if base_name.endswith('.tar'):
            base_name = base_name[:-4]
        
        # If maintaining hierarchy and archive is nested (not in source root)
        # extract in-place, otherwise extract as sibling
        if self.maintain_hierarchy and archive_path.parent != self.source_folder:
            # Extract nested archives in their current location
            return parent_dir / base_name
        else:
            # Extract to sibling directory
            return parent_dir / base_name
    
    def _extract_with_cleanup(self, archive_path, extract_to, extract_method):
        """Extract archive with automatic cleanup on failure"""
        created_extraction_dir = False
        
        try:
            # Remember what was there before
            existing_items = set(extract_to.iterdir()) if extract_to.exists() else set()
            
            # Create extraction directory if needed
            if not extract_to.exists():
                extract_to.mkdir(parents=True, exist_ok=True)
                created_extraction_dir = True
            
            # Attempt extraction
            success = extract_method(archive_path, extract_to)
            
            if not success:
                raise Exception("Extraction method returned False")
            
            # Verify something was actually extracted
            new_items = set(extract_to.iterdir()) - existing_items
            if not new_items:
                raise Exception("No files were extracted")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Extraction failed: {e}")
            print(f"  🧹 Cleaning up partial extraction...")
            
            # Clean up: remove newly created items
            try:
                if extract_to.exists():
                    current_items = set(extract_to.iterdir())
                    new_items = current_items - existing_items
                    
                    for item in new_items:
                        try:
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item)
                        except:
                            pass
                    
                    # Remove directory if we created it and it's now empty
                    if created_extraction_dir:
                        try:
                            if not list(extract_to.iterdir()):
                                extract_to.rmdir()
                        except:
                            pass
                    
                    self.stats['cleaned_up'] += 1
                    print(f"  ✓ Cleanup complete")
                        
            except Exception as cleanup_error:
                print(f"  ⚠️  Cleanup warning: {cleanup_error}")
            
            return False
    
    def _delete_archives(self):
        """Delete all successfully extracted archives at the end"""
        if not self.delete_after or not self.pending_deletions:
            return
        
        print(f"\n🗑️  Deleting {len(self.pending_deletions)} successfully extracted archive(s)...")
        print("   (This happens at the end to prevent data loss if interrupted)")
        print()
        
        for archive_path in self.pending_deletions:
            try:
                if archive_path.exists():
                    archive_path.unlink()
                    self.stats['deleted'] += 1
                    print(f"  ✓ {archive_path.name}")
            except Exception as e:
                print(f"  ✗ {archive_path.name}: {e}")
    
    def extract_all(self):
        """Recursively extract all archives"""
        self.start_time = datetime.now()
        
        print("=" * 60)
        print("  📂 Unfolder - Simple Archive Extractor")
        print("  Supports: ZIP, RAR, 7Z, TAR, GZ, BZ2")
        print("=" * 60)
        print(f"Source folder: {self.source_folder}")
        print(f"Delete after extraction: {self.delete_after}")
        print(f"Extraction mode: {'Nested (in-place)' if self.maintain_hierarchy else 'Flat (siblings)'}")
        
        # Show format support status
        if not HAS_7Z:
            print("  ℹ️  7Z support: Install py7zr for full support")
        if not HAS_RAR:
            print("  ℹ️  RAR support: Install rarfile for full support")
        print("")
        
        round_num = 1
        while True:
            # Find all archive files
            all_archives = []
            for root, dirs, files in os.walk(self.source_folder):
                for file in files:
                    file_path = Path(root) / file
                    if self._is_archive(file_path) and str(file_path) not in self.processed_files:
                        all_archives.append(file_path)
            
            if not all_archives:
                print("✅ No more archives found to extract")
                break
            
            print(f"\n--- Round {round_num}: Found {len(all_archives)} new archive(s) ---")
            
            for idx, archive_path in enumerate(all_archives, 1):
                # Mark as processed immediately to avoid infinite loops
                self.processed_files.add(str(archive_path))
                
                extract_to = self._get_extraction_path(archive_path)
                
                # Get file size for statistics
                file_size = self._get_file_size(archive_path)
                
                # Progress indicator
                print(f"\n📦 [{idx}/{len(all_archives)}] Extracting: {archive_path.name}")
                print(f"   From: {archive_path.parent}")
                print(f"   To:   {extract_to}")
                print(f"   Size: {self._format_size(file_size)}")
                
                # Extract archive with cleanup on failure
                extract_method = self._get_extract_method(archive_path)
                if extract_method and self._extract_with_cleanup(archive_path, extract_to, extract_method):
                    print(f"  ✅ Success")
                    self.stats['extracted'] += 1
                    self.stats['total_size'] += file_size
                    
                    # Queue for deletion (don't delete yet!)
                    if self.delete_after:
                        self.pending_deletions.append(archive_path)
                else:
                    self.stats['failed'] += 1
            
            round_num += 1
        
        # NOW delete if requested (after ALL extraction is complete)
        self._delete_archives()
        
        self._print_summary()
    
    def _print_summary(self):
        """Print extraction summary"""
        elapsed = datetime.now() - self.start_time
        elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
        
        print("\n" + "=" * 60)
        print("🎉 EXTRACTION COMPLETE!")
        print("=" * 60)
        print(f"📦 Archives extracted: {self.stats['extracted']}")
        print(f"❌ Failed extractions: {self.stats['failed']}")
        if self.stats['cleaned_up'] > 0:
            print(f"🧹 Failed archives cleaned up: {self.stats['cleaned_up']}")
        if self.delete_after:
            print(f"🗑️  Archives deleted: {self.stats['deleted']}")
        print(f"💾 Total size processed: {self._format_size(self.stats['total_size'])}")
        print(f"⏱️  Time elapsed: {elapsed_str}")
        
        # Calculate speed if we processed anything
        if self.stats['total_size'] > 0 and elapsed.total_seconds() > 0:
            speed = self.stats['total_size'] / elapsed.total_seconds()
            print(f"🚀 Average speed: {self._format_size(speed)}/s")
        
        print("=" * 60)


def preview_extraction(source_folder):
    """Show what would be extracted without actually doing it"""
    print("=" * 60)
    print("  🔍 DRY RUN MODE - Preview Only")
    print("=" * 60)
    print()
    
    # Create a temporary extractor just to use its helper methods
    temp_extractor = SimpleExtractor(source_folder)
    
    all_archives = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            file_path = Path(root) / file
            if temp_extractor._is_archive(file_path):
                all_archives.append(file_path)
    
    if not all_archives:
        print("❌ No archives found in this folder")
        return
    
    print(f"📦 Found {len(all_archives)} archive(s):\n")
    
    total_size = 0
    for i, archive in enumerate(all_archives, 1):
        size = temp_extractor._get_file_size(archive)
        total_size += size
        extract_to = temp_extractor._get_extraction_path(archive)
        
        print(f"{i}. {archive.name}")
        print(f"   Size: {temp_extractor._format_size(size)}")
        print(f"   From: {archive.parent}")
        print(f"   To:   {extract_to}")
        print()
    
    print(f"📊 Total size: {temp_extractor._format_size(total_size)}")
    print(f"⚠️  Note: Nested archives inside these will be found in subsequent rounds")
    print()
    print("💡 To proceed with extraction, run without --dry-run")


def get_folder_interactive():
    """Interactive folder selection with tkinter fallback"""
    # Try tkinter first
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="Select folder containing your archive files")
        root.destroy()
        if folder:
            return folder
    except ImportError:
        pass
    
    # Fallback to manual entry
    print("💡 GUI folder selection not available")
    print("💡 Please enter folder path manually:")
    while True:
        folder = input("Folder path: ").strip().strip('"').strip("'")
        if not folder:
            print("   Empty path. Please try again.")
            continue
        
        folder_path = Path(folder)
        if folder_path.exists():
            return str(folder_path.absolute())
        else:
            print(f"   Path '{folder}' does not exist. Please try again.")


def parse_arguments():
    """Parse command line arguments"""
    delete_after = None
    source_folder = None
    dry_run = False
    maintain_hierarchy = True  # Default to nested mode
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--delete' or arg == '-d':
            delete_after = True
        elif arg == '--no-delete':
            delete_after = False
        elif arg == '--dry-run' or arg == '--preview':
            dry_run = True
        elif arg == '--nested' or arg == '--hierarchy':
            maintain_hierarchy = True
        elif arg == '--flat':
            maintain_hierarchy = False
        elif arg == '--help' or arg == '-h':
            print_help()
            sys.exit(0)
        elif arg == '--version' or arg == '-v':
            print("Unfolder version 3.1")
            sys.exit(0)
        elif not arg.startswith('-') and not source_folder:
            source_folder = arg
        i += 1
    
    return source_folder, delete_after, dry_run, maintain_hierarchy


def print_help():
    """Print help message"""
    print("""
Unfolder - Simple Archive Extractor

Usage: python unfolder.py [folder] [options]

Arguments:
  folder              Path to folder containing archives (optional - will prompt if not provided)

Options:
  --delete, -d        Delete archives after successful extraction (at end of all rounds)
  --no-delete         Keep archives after extraction (default)
  --dry-run           Preview what would be extracted without actually extracting
  --preview           Same as --dry-run
  --nested            Extract nested archives in-place - maintains hierarchy (default)
  --hierarchy         Same as --nested
  --flat              Extract all archives as siblings (alternative mode)
  --help, -h          Show this help message
  --version, -v       Show version information

Examples:
  python unfolder.py                           # Interactive mode with GUI folder picker
  python unfolder.py /path/to/archives         # Extract archives in specified folder
  python unfolder.py /path/to/archives -d      # Extract and delete archives when done
  python unfolder.py --dry-run                 # Preview what would be extracted
  python unfolder.py /path/to/archives --nested  # Maintain archive hierarchy

Supported formats:
  ZIP, TAR, GZ, BZ2, TGZ, TAR.GZ, TAR.BZ2 (built-in)
  RAR (requires: pip install rarfile)
  7Z (requires: pip install py7zr)
""")


def main():
    """Main entry point"""
    print("📂 Unfolder - Simple Archive Extractor v3.1")
    print("=" * 50)
    print()
    
    # Parse arguments
    source_folder, delete_after, dry_run, maintain_hierarchy = parse_arguments()
    
    # Check Windows long path support if on Windows
    if sys.platform == 'win32':
        long_path_status = check_long_path_support_windows()
        print()
        
        # If long paths are disabled or unknown, offer PowerShell fallback
        if long_path_status == False:
            print("⚠️  To enable long paths (requires admin PowerShell):")
            print("   New-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem' `")
            print("                    -Name 'LongPathsEnabled' -Value 1 -PropertyType DWORD -Force")
            
            if offer_powershell_fallback():
                # User chose PowerShell script, we're done
                return
        elif long_path_status == None:
            print("💡 If you encounter long path errors, try the PowerShell version (unzipper.ps1)")
            print()
    
    # Get source folder
    if not source_folder:
        source_folder = get_folder_interactive()
        if not source_folder:
            print("❌ No folder selected. Exiting...")
            sys.exit(1)
    
    # Validate folder
    if not os.path.exists(source_folder):
        print(f"❌ Error: Folder '{source_folder}' does not exist")
        sys.exit(1)
    
    # Handle dry-run mode
    if dry_run:
        preview_extraction(source_folder)
        sys.exit(0)
    
    # Ask about deletion if not specified via command line
    if delete_after is None:
        print(f"📁 Source: {source_folder}")
        print()
        while True:
            response = input("🗑️  Delete archives after successful extraction? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                delete_after = True
                break
            elif response in ['n', 'no']:
                delete_after = False
                break
            else:
                print("   Please enter 'y' or 'n'")
        print()
    
    # Ask about extraction structure if not specified
    if not sys.argv[1:]:  # Only ask in fully interactive mode
        print("📁 Extraction structure:")
        print("  1. Nested - Maintain archive hierarchy (extract in-place) [default]")
        print("  2. Flat - Extract all archives as siblings (alternative)")
        print()
        while True:
            response = input("Choose structure (1/2) [1]: ").strip() or "1"
            if response == "1":
                maintain_hierarchy = True
                break
            elif response == "2":
                maintain_hierarchy = False
                break
            else:
                print("   Please enter '1' or '2'")
        print()
    
    print(f"📁 Source: {source_folder}")
    print(f"🗑️  Delete after: {delete_after}")
    print(f"📂 Mode: {'Nested (in-place)' if maintain_hierarchy else 'Flat (siblings)'}")
    print()
    
    # Create extractor and run
    extractor = SimpleExtractor(source_folder, delete_after, maintain_hierarchy)
    extractor.extract_all()


if __name__ == "__main__":
    main()
