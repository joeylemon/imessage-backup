from __future__ import annotations
import os
from pathlib import Path
from hashlib import sha1
import shutil
import sqlite3
import json
import tempfile
from turtle import back
import phonenumbers


class BackupTool:
    """
    Take in a iPhone backup directory and generate a zip file with the following structure:

    out.zip/
    -> messages.json
    -> contacts.json
    -> attachments/
       -> 0AB09373-F366-4D3B-85FC-1ABA33EE534F-jpeg-image-xIcbg.jpeg
       -> 3A5AD82C-1CE0-404E-86D4-149522201EDB-FullSizeRender.jpg
       -> ...

    The messages.json file contains entries with the following format:
    {"id": 24341, "chat_title": "Family Chat", "chat_identifier": "chat36260175973343405", "participants": ["+11111111111","+11111111111"], "sender": "+11111111111", "is_from_me": false, "text": "hello!", "date": 1480095057, "attachment_path": null}

    Similarly, the contacts.json file has the format:
    {"id": 1, "first_name": "Dad", "last_name": null, "identifiers": ["+1111111111"]}
    """

    def __init__(self, in_dir: str, out_file: str) -> None:
        self.in_dir = in_dir
        self.out_file = out_file

        # Apple stores sqlite database files in the backup directory
        self._messages_db_file = Path(
            in_dir, "3d", "3d0d7e5fb2ce288813306e4d4636395e047a3d28")
        self._contacts_db_file = Path(
            in_dir, "31", "31bb7ba8914766d4ba40d6dfb6113c8b614be442")

    def _read_file(self, file) -> str:
        with open(file, 'r') as f:
            output = f.read()
        return output

    def _get_messages(self) -> list[Message]:
        conn = sqlite3.connect(self._messages_db_file)
        conn.row_factory = Message.row_factory
        cursor = conn.cursor()
        query = self._read_file(
            Path(Path(__file__).parent, "sql", "get_messages.sql").resolve())
        cursor.execute(query)

        messages = cursor.fetchall()
        return messages

    def _get_contacts(self) -> list[Contact]:
        conn = sqlite3.connect(self._contacts_db_file)
        conn.row_factory = Contact.row_factory
        cursor = conn.cursor()
        query = self._read_file(
            Path(Path(__file__).parent, "sql", "get_contacts.sql").resolve())
        cursor.execute(query)

        contacts = cursor.fetchall()
        return contacts

    def run(self) -> None:
        """ Search the backup directory in_dir for messages and create a zip file at out_file. """
        try:
            messages = self._get_messages()
            contacts = self._get_contacts()

            # Create temporary directory structure
            tempdir = tempfile.mkdtemp()
            attachments_dir = Path(tempdir, "attachments")
            os.mkdir(attachments_dir)

            # Copy message attachments
            messages_with_attachments = [
                m for m in messages if m.attachment_path is not None]
            num_attachments = len(messages_with_attachments)
            for i, msg in enumerate(messages_with_attachments):
                try:
                    msg.copy_attachment(self.in_dir, attachments_dir)
                    if i % 100 == 0:
                        print(f"Copied attachment {i}/{num_attachments}")
                except FileNotFoundError as e:
                    # Print and continue
                    print(e)

            # Create messages.json
            messages_file = Path(tempdir, "messages.json")
            with open(messages_file, "w") as f:
                f.write(json.dumps(messages, indent=4))

            # Create contacts.json
            contacts_file = Path(tempdir, "contacts.json")
            with open(contacts_file, "w") as f:
                f.write(json.dumps(contacts, indent=4))

            # Build the .zip file of the backup data
            shutil.make_archive(Path(self.out_file), 'zip', tempdir)
        except Exception as e:
            print(f"an error occurred while backing up messages: {e}")
        finally:
            # Always delete the temporary directory
            shutil.rmtree(tempdir, ignore_errors=True)


class Message(dict):
    def __init__(self, id: int, chat_title: str, chat_identifier: str, participants: str, sender: str, is_from_me: int, text: str, date: int, attachment_path: str) -> None:
        self.id = id
        self.chat_title = chat_title
        self.chat_identifier = chat_identifier
        self.participants = participants.split(',')
        self.sender = sender
        self.is_from_me = is_from_me == 1
        self.text = text.strip()
        # After iOS11, epoch needs to be converted from nanoseconds to seconds and adjusted 31 years
        self.date = date // 1000**3 + 978307200
        self.attachment_path = attachment_path

        # Inherit dict to make JSON serialization easy
        dict.__init__(self, **self.__dict__)

    def get_attachment_source(self, in_dir: str) -> Path:
        """ Find the actual path to the attachment in the backup directory. """
        # Apple generates the backup directory structure by SHA1 hashing the path
        domainpath = "MediaDomain-" + self.attachment_path[2:]
        filename = sha1(domainpath.encode('utf-8')).hexdigest()

        # The backup directory is organized into subfolders using the first two digits of the hash
        dirname = filename[:2]

        filepath = Path(in_dir, dirname, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"error: failed to find attachment {self.attachment_path} at {filepath}")

        return filepath

    def copy_attachment(self, in_dir: str, out_dir: str) -> None:
        """ Copy the actual attachment to the given output directory. """
        if self.attachment_path is not None:
            src = self.get_attachment_source(in_dir)

            # e.g. convert ~/Library/SMS/Attachments/a8/08/5940B5EB-0BE7-4949-946E-3DDDFFC12366/IMG_3288.JPG
            #           to 5940B5EB-0BE7-4949-946E-3DDDFFC12366-IMG_3288.JPG
            dst = '-'.join(self.attachment_path.split('/')[-2:])
            dst = Path(out_dir, dst)

            self.attachment_path = str(dst)

            shutil.copy2(src, dst)

    @staticmethod
    def row_factory(cursor, row):
        return Message(*row)


class Contact(dict):
    def __init__(self, id: int, first_name: str, last_name: str, identifiers: str) -> None:
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

        self.identifiers = []
        numbers = identifiers.split(',')

        # Convert all phone number identifiers into standard E164 format
        for number in numbers:
            try:
                parsed_number = phonenumbers.parse(number, "US")
                formatted_number = phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.E164)
                self.identifiers.append(formatted_number)
            except phonenumbers.phonenumberutil.NumberParseException:
                self.identifiers.append(number)

        # Inherit dict to make JSON serialization easy
        dict.__init__(self, **self.__dict__)

    @staticmethod
    def row_factory(cursor, row):
        return Contact(*row)
