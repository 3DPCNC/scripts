# _____________________________________________________________________________

## **Duplicate File Finder**

The `Duplicate File Finder` script (`dupe_finder.py`) is a powerful and flexible tool designed to scan directories for files, identify duplicates using SHA-256 hashing, and organize unique and duplicate files into separate folders. It supports dynamic configuration, robust error handling, and efficient file processing, making it ideal for managing large datasets.

---

## **Features**

### 1. **Duplicate Detection**

- Uses **SHA-256 hashing** to identify duplicate files based on their content.
- Performs **byte-by-byte comparison** to confirm duplicates in case of hash collisions.

### 2. **Dynamic File Type Support**

- Allows users to specify file extensions to include during the scan (e.g., `.jpg`, `.png`, `.txt`).
- Supports files with unknown extensions or no extensions (e.g., `README`).

### 3. **Output Organization**

- Unique files are copied to a `UniqueFiles` folder.
- Duplicate files are copied to a `DuplicateFiles` folder.
- Unique files can be further organized into subdirectories by file type or file type groups (e.g., `Documents`, `Images`, `Audio`).

### 4. **Progress Tracking**

- Displays a **progress bar** using the `tqdm` library to show the scan's progress.

### 5. **Resilience**

- Handles interruptions gracefully by saving progress and resuming from where it left off.
- Logs errors and progress to a log file (`file_scan.log`).

### 6. **Database Integration**

- Uses **SQLite** to store file hashes for scalability and performance.
- Prevents reprocessing of files already scanned in previous runs.

### 7. **Disk Space Check**

- Ensures sufficient disk space is available before copying files.

### 8. **Dry-Run Mode**

- Simulates the scan without copying files or modifying the database, allowing users to preview the results.

---

## **Requirements**

### **Python Version**

- Python 3.6 or higher

### **Dependencies**

- `tqdm` (for progress bar)
- `sqlite3` (built into Python)
- `argparse` (built into Python)

Install `tqdm` using pip:

```bash
pip install tqdm
```

## **Usage**

### **Basic Command**

Run the script with default settings:

```bash
python dupe_finder.py
```

---

## **Command-Line Arguments**

The script supports the following arguments:

| Argument         | Description                                                                                     | Default Value              |
|------------------|-------------------------------------------------------------------------------------------------|----------------------------|
| `--extensions`   | File extensions to include (e.g., `.jpg .png .txt`).                                            | All supported extensions   |
| `--root-dir`     | Root directory to scan.                                                                         | `TestRoot`                 |
| `--output-dir`   | Output directory for unique and duplicate files.                                                | `TestRoot/FileScanTest`    |
| `--dry-run`      | Simulates the scan without copying files or modifying the database.                             | Disabled                   |
| `--clear-hashes` | Clears the hash database and progress file before starting.                                      | Disabled                   |

---

### **Examples**

#### **1. Scan for Image Files (Default Behavior)**

```bash
python dupe_finder.py 
```

- Scans the `TestRoot` directory for image files (`.jpg`, `.png`, etc.).
- Copies unique files to `TestRoot/FileScanTest/UniqueFiles`.
- Copies duplicates to `TestRoot/FileScanTest/DuplicateFiles`.

## **2. Scan for Specific File Types**

```bash
python dupe_finder.py --extensions .txt .log .md
```

- Scans for `.txt`, `.log`, and `.md` files.

## **3. Specify a Different Root Directory**

```bash
python dupe_finder.py --root-dir "E:/Documents"
```

- Scans the `E:/Documents` directory instead of the default.

### **4. Specify a Different Output Directory**

```bash
python dupe_finder.py --output-dir "E:/FileScanResults"
```

- Saves unique and duplicate files to `E:/FileScanResults`.

#### **5. Dry-Run Mode**

```bash
python dupe_finder.py --dry-run
```

- Simulates the scan without copying files or modifying the database.
- Logs actions that would be performed.

#### **6. Clear Hash Database**

```bash
python dupe_finder.py --clear-hashes
```

- Clears the hash database and progress file before starting the scan.

---

## **How It Works**

### **1. File Validation**

- Validates files based on their extensions or MIME types.
- Files with unknown extensions or no extensions are placed in the `"Other"` folder.

### **2. Duplicate Detection**

- Files are hashed using SHA-256 to generate a unique identifier for their content.
- If two files have the same hash, they are compared byte-by-byte to confirm they are identical.

### **3. File Copying**

- Unique files are copied to the `UniqueFiles` folder.
- Duplicates are copied to the `DuplicateFiles` folder.
- Ensures no filename conflicts by appending a numeric suffix to duplicate filenames.

### **4. Progress Tracking**

- Uses `tqdm` to display a progress bar, showing the number of files processed.

### **5. Database Integration**

- Stores file hashes in an SQLite database to avoid reprocessing files in subsequent runs.

### **6. Graceful Interrupt Handling**

- Saves progress and exits gracefully when interrupted (e.g., Ctrl+C).

---

## **Log File**

All progress and errors are logged to `file_scan.log`. Example log entries:

```plaintext
2025-04-18 13:20:57,853 - INFO - Moved example.jpg to TestRoot/FileScanTest/UniqueFiles/Images
2025-04-18 13:20:57,855 - WARNING - Skipping symbolic link: TestRoot/Link
2025-04-18 13:20:57,857 - ERROR - Error copying file3.jpg to destination
```

---

## **Known Limitations**

1. **Performance**:
   - Hashing and byte-by-byte comparisons can be slow for very large datasets. Consider increasing `CHUNK_SIZE` for better performance.

2. **File Extensions**:
   - Relies on file extensions for validation. Files without extensions are placed in the `"Other"` folder.

3. **Progress Bar Jumping**:
   - The progress bar dynamically adjusts its total when files are skipped, which may cause it to "jump."

---

## **Future Improvements**

1. Add support for multi-threaded file processing to improve performance.
2. Implement a configuration file for easier customization.
3. Add support for excluding specific subdirectories.
4. Create a graphical user interface (GUI) for non-technical users.

---

## **Conclusion**

The `Duplicate File Finder` script is a robust and efficient tool for managing duplicate files. By leveraging hashing, database integration, and dynamic configuration, it ensures reliable and scalable operation. Whether you're organizing personal files or managing large datasets, this script provides the flexibility and performance you need.
