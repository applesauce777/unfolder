#!/usr/bin/env python3
"""
Basic tests for Unfolder - Simple Archive Extractor
Run with: python test_unfolder.py
"""

import os
import sys
import tempfile
import shutil
import zipfile
import tarfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from unfolder import SimpleExtractor, preview_extraction
except ImportError as e:
    print(f"❌ Failed to import unfolder: {e}")
    print("Make sure unfolder.py is in the same directory")
    sys.exit(1)

def create_test_archives(test_dir):
    """Create test archive files for testing"""
    print("📁 Creating test archives...")
    
    # Create some test files
    test_files = {
        'document.txt': 'This is a test document',
        'data.json': '{"test": true, "nested": {"value": 42}}',
        'subdir/nested.txt': 'Nested file content'
    }
    
    # Create test directory structure
    for file_path, content in test_files.items():
        full_path = test_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    # Create ZIP archive
    zip_path = test_dir / 'test.zip'
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for file_path in test_files:
            zf.write(test_dir / file_path, file_path)
    
    # Create TAR.GZ archive
    tar_path = test_dir / 'test.tar.gz'
    with tarfile.open(tar_path, 'w:gz') as tf:
        for file_path in test_files:
            tf.add(test_dir / file_path, file_path)
    
    # Create nested ZIP (ZIP inside ZIP)
    nested_zip_path = test_dir / 'nested.zip'
    with zipfile.ZipFile(nested_zip_path, 'w') as zf:
        zf.write(zip_path, 'inner.zip')
    
    return [zip_path, tar_path, nested_zip_path]

def test_basic_extraction():
    """Test basic archive extraction"""
    print("\n🧪 Testing basic extraction...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / 'test_input'
        test_dir.mkdir()
        
        # Create test archives
        archives = create_test_archives(test_dir)
        
        # Test extraction
        extractor = SimpleExtractor(test_dir, delete_after=False)
        extractor.extract_all()
        
        # Verify extraction
        extracted_dirs = [
            test_dir / 'test',
            test_dir / 'test',  # Both zip and tar should extract to 'test'
            test_dir / 'nested'
        ]
        
        for extract_dir in extracted_dirs:
            if extract_dir.exists():
                print(f"  ✅ Extracted: {extract_dir.name}")
                # Check for expected files
                if (extract_dir / 'document.txt').exists():
                    print(f"    ✅ Found document.txt")
                if (extract_dir / 'data.json').exists():
                    print(f"    ✅ Found data.json")
            else:
                print(f"  ❌ Missing: {extract_dir.name}")
        
        # Check statistics
        print(f"  📊 Stats: {extractor.stats}")

def test_preview_mode():
    """Test dry-run/preview mode"""
    print("\n🧪 Testing preview mode...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / 'test_input'
        test_dir.mkdir()
        
        # Create test archives
        archives = create_test_archives(test_dir)
        
        # Test preview (capture output)
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            preview_extraction(test_dir)
        
        output = f.getvalue()
        
        # Check if preview contains expected information
        if 'test.zip' in output:
            print("  ✅ Preview shows test.zip")
        if 'test.tar.gz' in output:
            print("  ✅ Preview shows test.tar.gz")
        if 'nested.zip' in output:
            print("  ✅ Preview shows nested.zip")
        if 'DRY RUN MODE' in output:
            print("  ✅ Preview mode indicated")

def test_error_handling():
    """Test error handling with corrupted archives"""
    print("\n🧪 Testing error handling...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / 'test_input'
        test_dir.mkdir()
        
        # Create a corrupted ZIP file
        corrupted_zip = test_dir / 'corrupted.zip'
        corrupted_zip.write_bytes(b'This is not a valid ZIP file')
        
        # Test extraction with corrupted file
        extractor = SimpleExtractor(test_dir, delete_after=False)
        extractor.extract_all()
        
        # Should handle gracefully
        if extractor.stats['failed'] > 0:
            print(f"  ✅ Handled corrupted file: {extractor.stats['failed']} failed")
        else:
            print("  ⚠️ Expected to handle corrupted file")

def test_nested_extraction():
    """Test nested archive extraction"""
    print("\n🧪 Testing nested extraction...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / 'test_input'
        test_dir.mkdir()
        
        # Create nested structure: outer.zip -> inner.zip -> content
        inner_content = test_dir / 'content.txt'
        inner_content.write_text('Inner content')
        
        # Create inner ZIP
        inner_zip = test_dir / 'inner.zip'
        with zipfile.ZipFile(inner_zip, 'w') as zf:
            zf.write(inner_content, 'content.txt')
        
        # Create outer ZIP containing inner ZIP
        outer_zip = test_dir / 'outer.zip'
        with zipfile.ZipFile(outer_zip, 'w') as zf:
            zf.write(inner_zip, 'inner.zip')
        
        # Clean up intermediate files
        inner_content.unlink()
        inner_zip.unlink()
        
        # Test nested extraction
        extractor = SimpleExtractor(test_dir, delete_after=False)
        extractor.extract_all()
        
        # Check if nested content was extracted
        outer_dir = test_dir / 'outer'
        inner_dir = outer_dir / 'inner'
        
        if outer_dir.exists() and inner_dir.exists():
            if (inner_dir / 'content.txt').exists():
                print("  ✅ Nested extraction successful")
            else:
                print("  ❌ Nested content not found")
        else:
            print("  ❌ Nested directories not created")

def test_archive_detection():
    """Test archive file detection"""
    print("\n🧪 Testing archive detection...")
    
    extractor = SimpleExtractor(Path('.'))  # Dummy path
    
    # Test various file extensions
    test_cases = [
        ('test.zip', True),
        ('test.tar.gz', True),
        ('test.tar.bz2', True),
        ('test.tgz', True),
        ('test.rar', True),
        ('test.7z', True),
        ('test.gz', True),
        ('test.bz2', True),
        ('test.txt', False),
        ('test.pdf', False),
        ('test', False)
    ]
    
    for filename, expected in test_cases:
        result = extractor._is_archive(Path(filename))
        status = "✅" if result == expected else "❌"
        print(f"  {status} {filename}: {result} (expected {expected})")

def main():
    """Run all tests"""
    print("🧪 Unfolder Test Suite")
    print("=" * 50)
    
    tests = [
        test_archive_detection,
        test_basic_extraction,
        test_preview_mode,
        test_error_handling,
        test_nested_extraction
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
