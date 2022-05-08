import argparse
import os
from backup_tool import BackupTool


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backup messages from an iPhone")

    parser.add_argument(
        "input", help="the directory path containing the iPhone backup")
    parser.add_argument(
        "-o", "--out", help="the name of the output zip file", default="out")

    args = parser.parse_args()

    args.input = os.path.abspath(args.input)
    if not os.path.exists(args.input):
        print(f"path {args.input} does not exist")
        exit(1)
    elif not os.path.isdir(args.input):
        print(f"path {args.input} is not a directory")
        exit(1)

    return args


if __name__ == "__main__":
    args = get_args()
    tool = BackupTool(args.input, args.out)
    tool.run()
