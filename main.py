import argparse
import os
from pathlib import Path
from backup_tool import BackupTool
from utils import get_archive_format


"""
TODO:
- create archive_creator.py
    - save each unique chat into its own file
    - change the file modify date to last message
"""


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backup messages from an iPhone")

    parser.add_argument(
        "input", help="the directory path containing the iPhone backup")
    parser.add_argument(
        "-o", "--out", help="the name of the output file", default="out.zip")

    args = parser.parse_args()

    args.input = Path(args.input).resolve()
    if not os.path.exists(args.input):
        print(f"path {args.input} does not exist")
        exit(1)
    elif not os.path.isdir(args.input):
        print(f"path {args.input} is not a directory")
        exit(1)

    args.out = Path(args.out).resolve()
    try:
        get_archive_format(args.out)
    except ValueError as e:
        print(e)
        exit(1)

    return args


if __name__ == "__main__":
    args = get_args()
    tool = BackupTool(args.input, args.out)
    tool.run()
