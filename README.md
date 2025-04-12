# **README: Duplicate File Finder Script**

This script, dupe_finder.py, is designed to scan a directory for files with specified extensions, identify duplicates, and copy unique files to a designated folder while organizing duplicates into a separate folder. It uses file hashing (SHA-256) to detect duplicates and supports dynamic configuration via command-line arguments.

---

## **Features**

1. **Duplicate Detection**:
   - Uses SHA-256 hashing to identify duplicate files.
   - Compares files byte-by-byte if a hash collision is detected.

2. **Dynamic File Type Support**:
   - Specify file extensions to include during the scan (e.g., `.jpg`, `.png`, `.txt`).

3. **Output Organization**:
   - Unique files are copied to a `UniqueFiles` folder.
   - Duplicate files are copied to a `DuplicateFiles` folder.

4. **Progress Tracking**:
   - Displays a progress bar using `tqdm` to show the scan's progress.

5. **Dry-Run Mode**:
   - Simulates the scan without copying files or modifying the database.

6. **Resilience**:
   - Handles interruptions gracefully by saving progress.
   - Logs errors and progress to a log file (`file_scan.log`).

7. **Database Integration**:
   - Uses SQLite to store file hashes for scalability and performance.

8. **Disk Space Check**:
   - Ensures sufficient disk space is available before copying files.

---

## **Requirements**

- Python 3.6 or higher
- Required Python packages:
  - `tqdm`
  - `sqlite3` (built into Python)
  - `argparse` (built into Python)

Install `tqdm` if not already installed:

```bash
pip install tqdm
```

---

## **Usage**

### **Basic Command**

Run the script with default settings:

```bash
python dupe_finder.py
```

### **Command-Line Arguments**

The script supports the following command-line arguments:

| Argument         | Description                                                                                     | Default Value              |
|------------------|-------------------------------------------------------------------------------------------------|----------------------------|
| `--extensions`   | File extensions to include (e.g., `.jpg .png .txt`).                                            | `.jpg .jpeg .png .gif .bmp .tiff .webp` |
| `--root-dir`     | Root directory to scan.                                                                         | F:                      |
| `--output-dir`   | Output directory for unique and duplicate files.                                                | `D:/ImageScanTest`         |
| `--dry-run`      | Simulates the scan without copying files or modifying the database.                             | Disabled                   |

---

### **Examples**

#### **1. Scan for Image Files (Default Behavior)**

```bash
python dupe_finder.py
```

- Scans the F: directory for image files (`.jpg`, `.png`, etc.).
- Copies unique files to `D:/ImageScanTest/UniqueFiles`.
- Copies duplicates to `D:/ImageScanTest/DuplicateFiles`.

#### **2. Scan for Text Files**

```bash
python dupe_finder.py --extensions .txt .log .md
```

- Scans for `.txt`, `.log`, and `.md` files.

#### **3. Specify a Different Root Directory**

```bash
python dupe_finder.py --root-dir "E:/Documents"
```

- Scans the `E:/Documents` directory instead of the default F:.

#### **4. Specify a Different Output Directory**

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

---

## **How It Works**

### **1. File Validation**

The script validates files based on their extensions and MIME types:

```python
def is_valid_file(filename, extensions):
    ext = os.path.splitext(filename.lower())[1]
    if ext in extensions:
        return True
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type and any(mime_type.endswith(ext.strip(".")) for ext in extensions)
```

### **2. Duplicate Detection**

- Files are hashed using SHA-256:

  ```python
  def hash_file(filepath, chunk_size=65536):
      hasher = hashlib.sha256()
      with open(filepath, "rb") as f:
          for chunk in iter(lambda: f.read(chunk_size), b""):
              hasher.update(chunk)
      return hasher.hexdigest()
  ```

- If two files have the same hash, they are compared byte-by-byte to confirm they are identical:

  ```python
  def files_are_identical(file1, file2):
      with open(file1, "rb") as f1, open(file2, "rb") as f2:
          while True:
              chunk1 = f1.read(65536)
              chunk2 = f2.read(65536)
              if chunk1 != chunk2:
                  return False
              if not chunk1:
                  return True
  ```

### **3. File Copying**

- Unique files are copied to `UniqueFiles`.
- Duplicates are copied to `DuplicateFiles`.
- The script ensures no filename conflicts:

  ```python
  def safe_copy(src, dest_dir, hashes):
      base = os.path.basename(src)
      dest_path = os.path.join(dest_dir, base)
      i = 1
      while os.path.exists(dest_path):
          name, ext = os.path.splitext(base)
          dest_path = os.path.join(dest_dir, f"{name}_{i}{ext}")
          i += 1
      shutil.copy2(src, dest_path)
  ```

### **4. Progress Tracking**

- The script uses `tqdm` to display a progress bar:

  ```python
  with tqdm(total=total_files, desc="Processing files") as pbar:
      for dirpath, _, filenames in os.walk(root_dir):
          ...
          pbar.update(1)
  ```

### **5. Database Integration**

- File hashes are stored in an SQLite database for scalability:

  ```python
  def initialize_database(db_path="hashes.db"):
      conn = sqlite3.connect(db_path)
      cursor = conn.cursor()
      cursor.execute("CREATE TABLE IF NOT EXISTS hashes (hash TEXT PRIMARY KEY, filepath TEXT)")
      conn.commit()
      return conn
  ```

### **6. Graceful Interrupt Handling**

- The script saves progress and exits gracefully when interrupted:

  ```python
  def handle_interrupt_factory(hashes):
      def handle_interrupt(signal, frame):
          save_progress(hashes)
          sys.exit(0)
      return handle_interrupt
  ```

---

## **Error Handling**

- **File I/O Errors**: Errors during file hashing, copying, or progress saving are logged.
- **Disk Space Check**: Ensures sufficient disk space before copying files.
- **Database Errors**: Logs database initialization or query errors.

---

## **Log File**

- All progress and errors are logged to `file_scan.log`:

  ```plaintext
  2025-04-09 12:00:00 - INFO - Processing file 1/100: example.jpg
  2025-04-09 12:00:01 - WARNING - Hash collision detected between file1.jpg and file2.jpg
  2025-04-09 12:00:02 - ERROR - Error copying file3.jpg to destination
  ```

---

## **Known Limitations**

1. **Progress Bar Jumping**:
   - The progress bar dynamically adjusts its total when files are skipped, which may cause it to "jump."
   - This behavior is intentional and documented in the script.

2. **Performance**:
   - For very large datasets, hashing and byte-by-byte comparisons may be slow. Consider increasing `CHUNK_SIZE` for better performance.

3. **File Extensions**:
   - The script relies on file extensions for validation. Files without extensions may be skipped.

---

## **Future Improvements**

1. Add support for multi-threaded file processing to improve performance.
2. Implement a configuration file for easier customization.
3. Add support for excluding specific subdirectories.

---

## **Conclusion**

This script is a powerful and flexible tool for identifying and organizing duplicate files. By leveraging hashing, database integration, and dynamic configuration, it ensures efficient and reliable operation. Let me know if you have any questions or need further assistance!

The detailed comments or docstrings go **below the code they describe** because Python follows a convention where **docstrings** (triple-quoted strings) are placed **inside functions, classes, or modules** to describe their purpose, arguments, and behavior. This is a widely accepted practice in Python to make the code self-documenting and accessible through tools like `help()` or IDE tooltips.

---

### **Why Docstrings Go Inside Functions or Classes**

1. **Python Convention**:
   - Docstrings are part of the Python standard for documenting code. They are placed **inside** the function, class, or module they describe.
   - Example:

     ```python
     def example_function():
         """
         This is a docstring that describes the function.
         """
         pass
     ```

2. **Accessibility**:
   - Docstrings are accessible at runtime using the `help()` function or by inspecting the `__doc__` attribute of the function or class.
   - Example:

     ```python
     def example_function():
         """
         This function does something useful.
         """
         pass

     print(example_function.__doc__)
     # Output: This function does something useful.
     ```

3. **Readability**:
   - Placing the docstring inside the function or class makes it clear that the comment belongs to that specific block of code.
   - This improves readability and helps developers quickly understand the purpose of the function or class.

---

### **Why Regular Comments Go Above the Code**

For non-docstring comments (using `#`), the convention is to place them **above the code** they describe. This is because:

1. **Context**:
   - Comments above the code provide context before the code is executed.
   - Example:

     ```python
     # This function calculates the square of a number.
     def square(x):
         return x * x
     ```

2. **Separation**:
   - Placing comments above the code avoids mixing them with the logic inside the function or class, keeping the code clean and focused.

---

### **When to Use Docstrings vs. Comments**

- **Docstrings**:
  - Use for documenting the purpose, arguments, and return values of functions, classes, or modules.
  - Place them **inside** the function, class, or module.

- **Comments**:
  - Use for explaining specific lines or blocks of code that might be unclear.
  - Place them **above** the code they describe.

---

### **Example: Docstrings and Comments Together**

```python
# This function calculates the square of a number.
def square(x):
    """
    Calculates the square of a number.

    Args:
        x (int or float): The number to square.

    Returns:
        int or float: The square of the input number.
    """
    # Multiply the number by itself to get the square.
    return x * x
```

---

### **Final Thoughts**

- **Docstrings** go **inside** the function, class, or module they describe because they are part of Python's documentation system.
- **Comments** go **above** the code they describe to provide context or explain specific logic.
