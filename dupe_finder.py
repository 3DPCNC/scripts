import os  # Added for file and directory operations
import hashlib  # Added for hashing files
import shutil  # Added for file copying and moving
import signal  # Added for handling interrupts
import sys  # Added for system-specific parameters and functions
import logging  # Added for logging
import mimetypes  # Added for MIME type detection
import pickle  # Added for serialization and deserialization of objects
from tqdm import tqdm  # Added for progress bar
import argparse  # Added for dynamic file type support
import sqlite3  # Added for database support



# Folder paths
ROOT_DIR = "F:/"  # Root directory to scan
OUTPUT_DIR = os.path.join(ROOT_DIR, "ImageScanTest")  # Output directory on the same drive
UNIQUE_DIR = os.path.join(OUTPUT_DIR, "UniqueFiles")
DUPLICATE_DIR = os.path.join(OUTPUT_DIR, "DuplicateFiles")


# Check if root directory exists
if not os.path.exists(ROOT_DIR):
    print(f"Error: Root directory '{ROOT_DIR}' does not exist.")
    sys.exit(1)


# Logging configuration
logging.basicConfig(
    filename="file_scan.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Declarations
CHUNK_SIZE = 65536  # 64KB
SAVE_INTERVAL = 10  # Save progress every 10 files


# Default file types to include (can be overridden by user input)
DEFAULT_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
# DEFAULT_FILE_EXTENSIONS = {".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".mpg", ".mpeg", ".lrv", ".thm"}
# DEFAULT_FILE_EXTENSIONS = {".txt", ".log", ".md", ".csv", ".json", ".xml", ".html", ".css", ".js"}
# DEFAULT_FILE_EXTENSIONS = {".doc", ".docx", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx"}
# DEFAULT_FILE_EXTENSIONS = {".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z"}
# DEFAULT_FILE_EXTENSIONS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"}
# DEFAULT_FILE_EXTENSIONS = {".exe", ".msi", ".apk", ".dmg", ".iso", ".bin", ".img"}
# DEFAULT_FILE_EXTENSIONS = {".py", ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rb"}
# DEFAULT_FILE_EXTENSIONS = {".svg", ".ai", ".eps", ".psd", ".indd", ".xd", ".fig"}
# DEFAULT_FILE_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2", ".eot", ".svgz"}



# Create output folders if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UNIQUE_DIR, exist_ok=True)
os.makedirs(DUPLICATE_DIR, exist_ok=True)


def parse_arguments():
    """
    Parses command-line arguments for dynamic file type support.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Scan for duplicate files.")
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=list(DEFAULT_FILE_EXTENSIONS),
        help="File extensions to include (e.g., .txt .log .md). Default is image file types."
    )
    parser.add_argument(
        "--root-dir",
        default=ROOT_DIR,
        help="Root directory to scan. Default is F:/."
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        help="Output directory for unique and duplicate files. Default is D:/ImageScanTest."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the script without copying files or modifying the database."
    )
    return parser.parse_args()


# This function checks if the drive has enough free space for the operation.
def check_disk_space(path, required_space):
    """
    Checks if the drive at the given path has at least the required space.

    Args:
        path (str): The path on the drive to check.
        required_space (int): The minimum required free space in bytes.

    Returns:
        bool: True if there is enough free space, False otherwise.
    """
    total, used, free = shutil.disk_usage(path)
    return free >= required_space


# Check disk space before starting the scan
if not check_disk_space(OUTPUT_DIR, 100 * 1024 * 1024):  # 100MB threshold
    print("Insufficient disk space on the output drive.")
    sys.exit(1)


def hash_file(filepath, chunk_size=CHUNK_SIZE):
    """
    Generates a SHA-256 hash for the given file.

    Args:
        filepath (str): Path to the file to hash.
        chunk_size (int): Size of chunks to read from the file.

    Returns:
        str: The hexadecimal hash of the file, or None if an error occurs.
    """
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    except Exception as e:
        logging.error(f"Error hashing {filepath}: {e}")
        return None


def is_valid_file(filename, extensions):
    """
    Checks if a file is valid based on its extension or MIME type.

    Args:
        filename (str): The name of the file to check.
        extensions (set): A set of valid file extensions.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    ext = os.path.splitext(filename.lower())[1]
    if ext in extensions:
        return True
    
    # Check MIME type if extension is not found
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type and any(mime_type.endswith(ext.strip(".")) for ext in extensions)


def safe_copy(src, dest_dir, hashes):
    """
    Copies a file to the destination directory, ensuring no filename conflicts.
    Checks if the file already exists in the destination directory by comparing its hash.

    Args:
        src (str): Path to the source file.
        dest_dir (str): Path to the destination directory.
        hashes (dict): Dictionary of hashes to file paths.
    """
    base = os.path.basename(src)
    dest_path = os.path.join(dest_dir, base)
    src_hash = hash_file(src)  # Compute once
    if src_hash is None:
        return

    if not check_disk_space(OUTPUT_DIR, os.path.getsize(src)):
        logging.error(f"Insufficient disk space to copy {src}")
        return

    i = 1
    max_attempts = 1000
    while os.path.exists(dest_path) and i <= max_attempts:
        existing_hash = hash_file(dest_path)
        if existing_hash == src_hash:
            if not files_are_identical(dest_path, src):
                logging.warning(f"Hash collision detected between {dest_path} and {src}")
            else:
                logging.info(f"File already exists in destination: {dest_path}")
                return
            
        name, ext = os.path.splitext(base)
        dest_path = os.path.join(dest_dir, f"{name}_{i}{ext}")
        i += 1
    if i > max_attempts:
        logging.error(f"Exceeded maximum attempts to create a unique filename for {src}")
        return
    
    try:
        shutil.copy2(src, dest_path)
    except Exception as e:
        logging.error(f"Error copying {src} to {dest_path}: {e}")
        print(f"Error copying {src} to {dest_path}: {e}")


def scan_and_copy_files(root_dir, extensions):
    """
    Scans a directory for files with specified extensions, identifies duplicates,
    and copies them to appropriate folders.

    Unique files are copied to the UNIQUE_DIR, while duplicates are copied to the DUPLICATE_DIR.
    Duplicate detection is based on file content hashes.

    Args:
        root_dir (str): The root directory to scan for files.
        extensions (set): A set of valid file extensions.

    Returns:
        tuple: (processed_files, skipped_files)
    """
    # Precompute total_files accurately
    total_files = sum(
        1 for dirpath, _, filenames in os.walk(root_dir)
        for fname in filenames if is_valid_file(fname, extensions) and not fname.startswith(".")
    )

    conn = initialize_database()
    hashes = load_hashes_from_db(conn)
    skipped_files = 0
    processed_files = 0

    # Register the signal handler with the current 'hashes'
    signal.signal(signal.SIGINT, handle_interrupt_factory(hashes))

    with tqdm(total=total_files, desc="Processing files") as pbar:
        for dirpath, _, filenames in os.walk(root_dir):
            if os.path.islink(dirpath):
                logging.warning(f"Skipping symbolic link: {dirpath}")
                continue

            # Skip the output directories to avoid redundant checks.
            if os.path.commonpath([os.path.abspath(dirpath), os.path.abspath(UNIQUE_DIR)]) == os.path.abspath(UNIQUE_DIR) or \
               os.path.commonpath([os.path.abspath(dirpath), os.path.abspath(DUPLICATE_DIR)]) == os.path.abspath(DUPLICATE_DIR):
                continue

            batch_count = 0
            for fname in filenames:
                if not is_valid_file(fname, extensions) or fname.startswith("."):
                    continue

                pbar.update(1)
                processed_files += 1
                logging.info(f"Processing file {processed_files}/{total_files}: {fname}")
                fpath = os.path.join(dirpath, fname)
                h = hash_file(fpath)
                if h is None:
                    skipped_files += 1
                    continue

                if args.dry_run:
                    logging.info(f"Dry-run: Would copy {fpath} to {UNIQUE_DIR if h not in hashes else DUPLICATE_DIR}")
                    continue

                if h not in hashes:
                    hashes[h] = fpath
                    save_hash_to_db(conn, h, fpath, batch_mode=True)
                    batch_count += 1
                    if batch_count % SAVE_INTERVAL == 0:
                        conn.commit()  # Commit every SAVE_INTERVAL files
                    safe_copy(fpath, UNIQUE_DIR, hashes)
                else:
                    safe_copy(fpath, DUPLICATE_DIR, hashes)
                    logging.info(f"Duplicate found: {fpath} (matches {hashes[h]})")
                if processed_files % SAVE_INTERVAL == 0:  # Save progress every SAVE_INTERVAL files
                    save_progress(hashes)
    conn.commit()  # Final commit at the end
    save_progress(hashes)
    logging.info(f"Total files skipped due to errors: {skipped_files}")
    conn.close()  # Close the database connection
    return processed_files, skipped_files


def files_are_identical(file1, file2):
    """
    Compares two files byte by byte to determine if they are identical.

    Args:
        file1 (str): Path to the first file.
        file2 (str): Path to the second file.

    Returns:
        bool: True if the files are identical, False otherwise.
    """
    try:
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            while True:
                chunk1 = f1.read(CHUNK_SIZE)
                chunk2 = f2.read(CHUNK_SIZE)
                if chunk1 != chunk2:
                    return False
                if not chunk1:  # End of file reached.
                    return True
    except Exception as e:
        logging.error(f"Error comparing {file1} and {file2}: {e}")
        return False


def save_progress(hashes, filename="hashes.pkl"):
    """
    Saves the current state of hashes to a file using pickle.
    """
    try:
        with open(filename, "wb") as f:
            pickle.dump(hashes, f)
    except Exception as e:
        logging.error(f"Error saving progress to {filename}: {e}")


def handle_interrupt_factory(hashes):
    """
    Creates a signal handler for graceful exit on interrupt.
    """
    def handle_interrupt(signal, frame):
        print("\nScript interrupted. Saving progress and exiting gracefully...")
        save_progress(hashes)
        sys.exit(0)
    return handle_interrupt


def load_progress(filename="hashes.pkl"):
    """
    Load progress data from a pickle file.

    This function attempts to load a dictionary of progress data from the specified
    pickle file. If the file does not exist or an error occurs during loading, 
    an empty dictionary is returned.

    Args:
        filename (str): The name of the pickle file to load. Defaults to "hashes.pkl".

    Returns:
        dict: The loaded progress data as a dictionary, or an empty dictionary if
              the file does not exist or an error occurs.
    """
    try:
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return pickle.load(f)
    except Exception as e:
        logging.error(f"Error loading progress from {filename}: {e}")
    return {}


def initialize_database(db_path="hashes.db"):
    """
    Initializes a SQLite database to store file hashes and their corresponding file paths.

    Args:
        db_path (str): The path to the SQLite database file. Defaults to "hashes.db".

    Returns:
        sqlite3.Connection: A connection object to the initialized SQLite database.

    Raises:
        SystemExit: If an SQLite error occurs during initialization, the program logs the error and exits.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS hashes (hash TEXT PRIMARY KEY, filepath TEXT)")
        conn.commit()
        return conn
    except sqlite3.Error as e:
        logging.error(f"Error initializing database: {e}")
        sys.exit(1)


def save_hash_to_db(conn, hash_value, filepath, batch_mode=False):
    """
    Saves a hash value and its associated file path to the database.

    This function inserts a hash value and its corresponding file path into the
    `hashes` table of the database. If the `batch_mode` parameter is set to False,
    the changes are committed immediately. Otherwise, the commit is deferred,
    allowing for batch processing.

    Args:
        conn (sqlite3.Connection): The database connection object.
        hash_value (str): The hash value to be stored.
        filepath (str): The file path associated with the hash value.
        batch_mode (bool, optional): If True, defers committing the transaction.
                                     Defaults to False.

    """
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO hashes (hash, filepath) VALUES (?, ?)", (hash_value, filepath))
    if not batch_mode:
        conn.commit()


def load_hashes_from_db(conn):
    """
    Loads file hashes and their corresponding file paths from the database.

    Args:
        conn (sqlite3.Connection): A connection object to the SQLite database.

    Returns:
        dict: A dictionary where the keys are file hashes (str) and the values are file paths (str).
    """
    cursor = conn.cursor()
    cursor.execute("SELECT hash, filepath FROM hashes")
    return dict(cursor.fetchall())


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    # Update global variables based on user input
    ROOT_DIR = args.root_dir
    OUTPUT_DIR = args.output_dir
    UNIQUE_DIR = os.path.join(OUTPUT_DIR, "UniqueFiles")
    DUPLICATE_DIR = os.path.join(OUTPUT_DIR, "DuplicateFiles")
    os.makedirs(UNIQUE_DIR, exist_ok=True)
    os.makedirs(DUPLICATE_DIR, exist_ok=True)

    # Convert extensions to a set
    FILE_EXTENSIONS = set(args.extensions)

    # Check if root directory exists
    if not os.path.exists(ROOT_DIR):
        print(f"Error: Root directory '{ROOT_DIR}' does not exist.")
        sys.exit(1)

    # Check disk space
    if not check_disk_space(OUTPUT_DIR, 100 * 1024 * 1024):  # 100MB threshold
        print("Insufficient disk space on the output drive.")
        sys.exit(1)

    # Start the scan
    print("Starting scan...")
    processed_files, skipped_files = scan_and_copy_files(ROOT_DIR, FILE_EXTENSIONS)
    print("Scan complete.")
    print(f"Total files processed: {processed_files}")
    print(f"Unique files copied to: {UNIQUE_DIR}")
    print(f"Duplicate files copied to: {DUPLICATE_DIR}")
    print(f"Total files skipped due to errors: {skipped_files}")
