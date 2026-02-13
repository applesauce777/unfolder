#!/usr/bin/env python3
"""
Create example archive files for testing Unfolder
Run with: python create_examples.py
"""

import os
import zipfile
import tarfile
from pathlib import Path

def create_simple_nested():
    """Create simple nested archive structure"""
    print("📁 Creating simple_nested.zip...")
    
    # Create content files
    with zipfile.ZipFile('examples/simple_nested.zip', 'w') as outer_zip:
        # Create documents.zip
        with zipfile.ZipFile('temp_documents.zip', 'w') as docs_zip:
            docs_zip.writestr('report.pdf', 'Fake PDF content')
            docs_zip.writestr('notes.txt', 'Meeting notes from 2023')
        
        outer_zip.write('temp_documents.zip', 'documents.zip')
        
        # Create photos.zip
        with zipfile.ZipFile('temp_photos.zip', 'w') as photos_zip:
            photos_zip.writestr('vacation.jpg', 'Fake JPG content')
            photos_zip.writestr('family.png', 'Fake PNG content')
        
        outer_zip.write('temp_photos.zip', 'photos.zip')
    
    # Clean up temp files
    os.remove('temp_documents.zip')
    os.remove('temp_photos.zip')

def create_google_takeout_demo():
    """Create Google Takeout demo structure"""
    print("📁 Creating google_takeout_demo.zip...")
    
    with zipfile.ZipFile('examples/google_takeout_demo.zip', 'w') as takeout_zip:
        # Drive folder
        with zipfile.ZipFile('temp_drive_docs.zip', 'w') as drive_docs:
            drive_docs.writestr('report_2023.docx', 'Document content')
            drive_docs.writestr('budget_2023.xlsx', 'Spreadsheet content')
        
        with zipfile.ZipFile('temp_drive_sheets.zip', 'w') as drive_sheets:
            drive_sheets.writestr('data_analysis.csv', 'CSV data')
            drive_sheets.writestr('charts.xlsx', 'Chart data')
        
        takeout_zip.write('temp_drive_docs.zip', 'Drive/documents.zip')
        takeout_zip.write('temp_drive_sheets.zip', 'Drive/spreadsheets.zip')
        
        # Photos folder
        with zipfile.ZipFile('temp_photos_2021.zip', 'w') as photos_2021:
            photos_2021.writestr('january/beach.jpg', 'Beach photo')
            photos_2021.writestr('february/skiing.jpg', 'Skiing photo')
        
        with zipfile.ZipFile('temp_photos_2022.zip', 'w') as photos_2022:
            photos_2022.writestr('summer/camping.jpg', 'Camping photo')
            photos_2022.writestr('winter/holidays.jpg', 'Holiday photo')
        
        takeout_zip.write('temp_photos_2021.zip', 'Photos/2021.zip')
        takeout_zip.write('temp_photos_2022.zip', 'Photos/2022.zip')
        
        # Location History
        with zipfile.ZipFile('temp_location.zip', 'w') as location:
            location.writestr('Location History.json', '{"locations": [{"lat": 40.7128, "lon": -74.0060}]}')
        
        takeout_zip.write('temp_location.zip', 'Location History/Location History.zip')
    
    # Clean up temp files
    os.remove('temp_drive_docs.zip')
    os.remove('temp_drive_sheets.zip')
    os.remove('temp_photos_2021.zip')
    os.remove('temp_photos_2022.zip')
    os.remove('temp_location.zip')

def create_deeply_nested():
    """Create deeply nested archive"""
    print("📁 Creating deeply_nested.zip...")
    
    # Start with innermost content
    Path('temp_level5').mkdir(exist_ok=True)
    with open('temp_level5/final_content.txt', 'w') as f:
        f.write('This is the final content at level 5!')
    
    # Level 5: Create innermost ZIP
    with zipfile.ZipFile('temp_level5.zip', 'w') as zip5:
        zip5.write('temp_level5/final_content.txt', 'final_content.txt')
    
    # Level 4: ZIP containing level 5
    with zipfile.ZipFile('temp_level4.zip', 'w') as zip4:
        zip4.write('temp_level5.zip', 'level5.zip')
    
    # Level 3: ZIP containing level 4
    with zipfile.ZipFile('temp_level3.zip', 'w') as zip3:
        zip3.write('temp_level4.zip', 'level4.zip')
    
    # Level 2: ZIP containing level 3
    with zipfile.ZipFile('temp_level2.zip', 'w') as zip2:
        zip2.write('temp_level3.zip', 'level3.zip')
    
    # Level 1: Final outer ZIP containing level 2
    with zipfile.ZipFile('examples/deeply_nested.zip', 'w') as zip1:
        zip1.write('temp_level2.zip', 'level1.zip')
    
    # Clean up
    import shutil
    shutil.rmtree('temp_level5')
    os.remove('temp_level5.zip')
    os.remove('temp_level4.zip')
    os.remove('temp_level3.zip')
    os.remove('temp_level2.zip')

def create_mixed_formats():
    """Create archive with mixed formats (ZIP only for demo)"""
    print("📁 Creating mixed_formats.zip...")
    
    with zipfile.ZipFile('examples/mixed_formats.zip', 'w') as mixed_zip:
        # Simulate different formats with appropriate content
        mixed_zip.writestr('data.tar.gz', 'Simulated TAR.GZ content')
        mixed_zip.writestr('backup.7z', 'Simulated 7Z content')
        mixed_zip.writestr('documents.rar', 'Simulated RAR content')
        mixed_zip.writestr('logs.zip', 'Simulated nested ZIP content')
        
        # Add a real nested ZIP for demonstration
        with zipfile.ZipFile('temp_logs.zip', 'w') as logs:
            logs.writestr('app.log', 'Application log content')
            logs.writestr('error.log', 'Error log content')
        
        mixed_zip.write('temp_logs.zip', 'logs.zip')
    
    os.remove('temp_logs.zip')

def main():
    """Create all example archives"""
    print("🗂️ Creating Unfolder Example Archives")
    print("=" * 50)
    
    # Ensure examples directory exists
    Path('examples').mkdir(exist_ok=True)
    
    # Create all examples
    create_simple_nested()
    create_google_takeout_demo()
    create_deeply_nested()
    create_mixed_formats()
    
    print("\n✅ All example archives created!")
    print("📁 Location: examples/ folder")
    print("\n🧪 Test with:")
    print("  python unfolder.py examples/ --dry-run")
    print("  python unfolder.py examples/")

if __name__ == "__main__":
    main()
