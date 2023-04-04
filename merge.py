import argparse
import os
import re
import shutil


PATTERN = re.compile(r"Week(\d{2})")
PDF_NAME = "notes.pdf"

def extract_dirs(src: str, start: int, end: int) -> list[str]:
    """Extract all week directories that are between start and end.

    Args:
        src (str): Source directory.
        start (int): Start week.
        end (int): End week.

    Returns:
        list[str]: List of directories.
    """    

    dirs = os.listdir(src)
    dirs = map(lambda dir: re.match(PATTERN, dir), dirs)
    dirs = filter(lambda dir: dir != None, dirs)
    dirs = filter(lambda dir: start <= int(dir.group(1)) <= end, dirs)
    dirs = map(lambda dir: dir.group(0), dirs)

    return sorted(dirs)

def copy_dirs(src: str, dest: str, dirs: list[str]):
    """Copy all the directories from the source to the destination.

    Args:
        src (str): Source directory.
        dest (str): Destination directory.
        dirs (list[str]): List of directories to copy.
    """

    if os.path.exists(dest):
        shutil.rmtree(dest)

    os.mkdir(dest)

    for dir in dirs:
        path = os.path.join(src, dir)
        # Check if the directory is not empty
        if len(os.listdir(path)) > 0:
            # Copy the directory to the destination
            shutil.copytree(path, dest, dirs_exist_ok=True)

def generate_pdf(dest: str):
    """Generate a pdf file from all the markdown files in the destination directory.

    Args:
        dest (str): Destination directory.
    """    

    # Get the current directory
    cwd = os.getcwd()

    os.chdir(dest)
    os.system("cat *.md > notes.md")
    os.system(f"pandoc notes.md -o {PDF_NAME}")

    # Go back to the original directory
    os.chdir(cwd)

def clean(dest: str):
    """Clean the destination directory.

    Args:
        dest (str): Destination directory.
    """    

    os.chdir(dest)
    for path in os.listdir():
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif path != PDF_NAME:
            os.remove(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merges all markdown files to a single pdf file.")
    parser.add_argument("src", type=str, help="Source directory.")
    parser.add_argument("dest", type=str, help="Destination directory.")
    parser.add_argument("start", type=int, help="Start week number.")
    parser.add_argument("end", type=int, help="End week number.")

    args = parser.parse_args()

    dirs = extract_dirs(args.src, args.start, args.end)
    copy_dirs(args.src, args.dest, dirs)
    generate_pdf(args.dest)
    clean(args.dest)

