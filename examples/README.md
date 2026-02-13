# 📂 Unfolder Examples

This folder contains example archive files to test Unfolder's capabilities.

## 🗂️ Example Files

### `simple_nested.zip`
A simple nested archive structure:
```
simple_nested.zip
├── documents.zip
│   ├── report.pdf
│   └── notes.txt
└── photos.zip
    ├── vacation.jpg
    └── family.png
```

### `google_takeout_demo.zip`
Simulates a Google Takeout export structure:
```
google_takeout_demo.zip
├── Drive/
│   ├── documents.zip
│   └── spreadsheets.zip
├── Photos/
│   ├── 2021.zip
│   │   ├── january.zip
│   │   └── february.zip
│   └── 2022.zip
└── Location History/
    └── Location History.zip
```

### `deeply_nested.zip`
Tests maximum nesting depth:
```
deeply_nested.zip
├── level1.zip
    ├── level2.zip
        ├── level3.zip
            ├── level4.zip
                ├── level5.zip
                    └── final_content.txt
```

### `mixed_formats.zip`
Contains different archive formats:
```
mixed_formats.zip
├── data.tar.gz
├── backup.7z
├── documents.rar
└── logs.zip
```

## 🧪 Testing Commands

### Basic Extraction
```bash
python unfolder.py examples/
```

### Preview Mode
```bash
python unfolder.py examples/ --dry-run
```

### With Deletion
```bash
python unfolder.py examples/ --delete
```

### Flat vs Nested Mode
```bash
# Nested (default - maintains hierarchy)
python unfolder.py examples/ --nested

# Flat (all as siblings)
python unfolder.py examples/ --flat
```

## 📊 Expected Results

- **simple_nested.zip**: Should extract 4 archives, create document and photo folders
- **google_takeout_demo.zip**: Should extract all nested archives, maintain Google Takeout structure
- **deeply_nested.zip**: Should extract all 5 levels, end with final_content.txt
- **mixed_formats.zip**: Should extract all formats (if optional dependencies installed)

## 🔍 Verification

After extraction, verify:
1. All expected files are present
2. Folder structure matches your chosen mode (nested/flat)
3. No corrupted or partial files
4. Statistics summary looks reasonable

## ⚠️ Note

These are test archives with small dummy files. Real-world archives may be much larger and more complex.
