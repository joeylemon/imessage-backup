import argparse
import os
import mimetypes
from backup_tool import BackupTool
from gen_tool import GenTool


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backup messages from an iPhone")
    subparsers = parser.add_subparsers(dest='command')

    # Backup command
    backup_parser = subparsers.add_parser(
        'backup', help='backup all messages from an iPhone backup')
    backup_parser.add_argument(
        "input", help="the directory path containing the iPhone backup")
    backup_parser.add_argument(
        "-o", "--out", help="the name of the output zip file", default="out")

    # Generate command
    gen_parser = subparsers.add_parser(
        'gen', help='generate a webpage to easily view messages')
    gen_parser.add_argument(
        "input", help="the zip file containing the backed up messages")
    gen_parser.add_argument(
        "-o", "--out", help="the directory path containing the iPhone backup", default="out")

    args = parser.parse_args()

    if args.command is None:
        parser.print_usage()
        exit(1)

    args.input = os.path.abspath(args.input)
    if not os.path.exists(args.input):
        print(f"path {args.input} does not exist")
        exit(1)

    return args


if __name__ == "__main__":
    args = get_args()

    if args.command == "backup":
        if not os.path.isdir(args.input):
            print(f"path {args.input} is not a directory")
            exit(1)

        tool = BackupTool(args.input, args.out)
        tool.run()
    elif args.command == "gen":
        if not os.path.isfile(args.input):
            print(f"path {args.input} is not a file")
            exit(1)
        elif mimetypes.MimeTypes().guess_type(args.input)[0] != "application/zip":
            print(f"path {args.input} is not a zip file")
            exit(1)

        tool = GenTool()
