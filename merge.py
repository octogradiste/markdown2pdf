import argparse
import os
import re
import shutil


PATTERN = re.compile(r"Week(\d{2})")
# PDF_NAME = "notes.pdf"

MARGIN_HEADER = '''geometry: margin=2cm
'''

WRAP_HEADER = '''header-includes:
 - \\usepackage{fvextra}
 - \\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\\\\{\\}}
'''

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

def generate_pdf(dest: str, lecture: bool, margin: bool, wrap_code: bool, pdf_name: str, start: int):
    """Generate a pdf file from all the markdown files in the destination directory.

    Args:
        dest (str): Destination directory.
        lecture (bool): Whether to include the "Lecture #week" before all files. Note that if the week number can't be extracted from the file name, a simple week counter will be used instead.
        margin (bool): Whether to add a margin to the pdf.
        wrap_code (bool): Whether to wrap the code in a code block.
        pdf_name (str): Output pdf file name.
        start (int): Start week.
    """    

    # Get the current directory

    concat = "---\n"
    if margin:
        concat += MARGIN_HEADER
    if wrap_code:
        concat += WRAP_HEADER
    concat += "---\n"

    week = start
    for path in sorted(os.listdir(dest)):
        if path.endswith(".md"):
            if lecture:
                pattern = re.compile(r"lecture_(\d{2}).md")
                match = re.match(pattern, path)
                if match != None:
                    # Prefer week number from file path over week counter.
                    week = int(match.group(1))

                concat += f"# Lecture {week}\n\n"
                week += 1

            full_path = os.path.join(dest, path)
            with open(full_path, "r") as f:
                concat += f.read()
            
            concat += "\n\n"

    full_path = os.path.join(dest, "notes.md")
    with open(full_path, "w") as f:
        f.write(concat)

    cwd = os.getcwd()
    os.chdir(dest)
    # os.system("cat *.md > notes.md")
    os.system(f"pandoc notes.md -o {pdf_name}")

    # Go back to the original directory
    os.chdir(cwd)

def clean(dest: str, pdf_name: str):
    """Clean the destination directory.

    Args:
        dest (str): Destination directory.
    """    

    os.chdir(dest)
    for path in os.listdir():
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif path != pdf_name:
            os.remove(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merges all markdown files to a single pdf file.")
    parser.add_argument("src", type=str, help="Source directory.")
    parser.add_argument("dest", type=str, help="Destination directory.")
    parser.add_argument("start", type=int, help="Start week number.")
    parser.add_argument("end", type=int, help="End week number.")
    parser.add_argument("-c", "--clean", action="store_true", help="Clean the destination directory.")
    parser.add_argument("-l", "--lecture", action="store_true", help="Add the lecture number before each file.")
    parser.add_argument("-w", "--wrap", action="store_true", help="Wrap the code in a code block.")
    parser.add_argument("-m", "--margin", action="store_true", help="Add a margin to the pdf.")
    parser.add_argument("-o", "--output", type=str, help="Output file name.", default="notes.pdf")

    args = parser.parse_args()

    dirs = extract_dirs(args.src, args.start, args.end)
    copy_dirs(args.src, args.dest, dirs)
    generate_pdf(args.dest, args.lecture, args.margin, args.wrap, args.output, args.start)

    if args.clean:
        clean(args.dest, args.output)

