import os
import random
import string

def generate_fake_files(root_dir, file_types, num_files=100):
    """
    Generates a set of fake files with various extensions for testing.

    Args:
        root_dir (str): The root directory where the files will be created.
        file_types (list): A list of file extensions to use for the fake files.
        num_files (int): The total number of files to generate.
    """
    os.makedirs(root_dir, exist_ok=True)
    for _ in range(num_files):
        # Generate a random filename
        filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        ext = random.choice(file_types)
        file_path = os.path.join(root_dir, f"{filename}{ext}")

        # Write some dummy content to the file
        with open(file_path, "w") as f:
            f.write(f"This is a test file with extension {ext}.\n")
            f.write("".join(random.choices(string.ascii_letters + string.digits, k=100)))

    print(f"Generated {num_files} fake files in {root_dir}")

# Define the root directory and file types
test_root_dir = "TestRoot"
file_extensions = [
    ".txt", ".log", ".md", ".csv", ".json", ".xml", ".html", ".css", ".js",
    ".doc", ".docx", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma",
    ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".mpg", ".mpeg",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z",
    ".exe", ".msi", ".apk", ".dmg", ".iso", ".bin", ".img",
    ".py", ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rb",
    ".stl", ".obj", ".gcode"  # Add 3D printing file extensions
]

# Generate the fake files
generate_fake_files(test_root_dir, file_extensions, num_files=20)