from __future__ import annotations
from pathlib import Path
from hashlib import sha1
from alive_progress import alive_it
import os
import shutil
import sqlite3
import json
import tempfile
import time
import phonenumbers
import utils


class BackupTool:
    """Take an iPhone backup directory and generate an archive file with the backed up messages."""

    def __init__(self, in_dir: str, out_file: str) -> None:
        self.in_dir = in_dir
        self.out_file = out_file

        # Apple stores sqlite database files in the backup directory
        self._messages_db_file = Path(in_dir, "3d", "3d0d7e5fb2ce288813306e4d4636395e047a3d28")
        self._contacts_db_file = Path(in_dir, "31", "31bb7ba8914766d4ba40d6dfb6113c8b614be442")

    def _get_messages(self) -> list[Message]:
        """ Execute the get_messages.sql query and store in a list of Messages. """
        conn = sqlite3.connect(self._messages_db_file)
        conn.row_factory = Message.row_factory
        cursor = conn.cursor()
        query = utils.read_file(Path(Path(__file__).parent, "sql", "get_messages.sql").resolve())
        cursor.execute(query)
        return cursor.fetchall()

    def _get_contacts(self) -> list[Contact]:
        """ Execute the get_contacts.sql query and store in a list of Contacts. """
        conn = sqlite3.connect(self._contacts_db_file)
        conn.row_factory = Contact.row_factory
        cursor = conn.cursor()
        query = utils.read_file(Path(Path(__file__).parent, "sql", "get_contacts.sql").resolve())
        cursor.execute(query)
        return cursor.fetchall()

    def _get_chats(self) -> list[Chat]:
        """ Execute the get_chats.sql query and store in a list of Chats. """
        conn = sqlite3.connect(self._messages_db_file)
        conn.row_factory = Chat.row_factory
        cursor = conn.cursor()
        query = utils.read_file(Path(Path(__file__).parent, "sql", "get_chats.sql").resolve())
        cursor.execute(query)
        return cursor.fetchall()

    def run(self) -> None:
        """ Search the backup directory in_dir for messages and create an archive file at out_file. """
        temp_dir = tempfile.mkdtemp()
        try:
            messages = self._get_messages()
            contacts = self._get_contacts()
            chats = self._get_chats()

            # Create temporary directory structure
            attachments_dir = Path(temp_dir, "attachments")
            chats_dir = Path(temp_dir, "chats")
            os.mkdir(attachments_dir)
            os.mkdir(chats_dir)

            # Copy message attachments
            messages_with_attachments = [m for m in messages if m.attachment_path is not None]
            for msg in alive_it(messages_with_attachments, title="Copy attachments"):
                try:
                    msg.copy_attachment(self.in_dir, attachments_dir)
                except Exception as e:
                    # Print and continue
                    print(e)

            # Create a file for each conversation
            for chat in alive_it(chats, title="Copy conversations"):
                chat_messages = [m.to_dict() for m in messages if m.chat_identifier == chat.chat_identifier]
                with open(Path(chats_dir, f"chat_{chat.id}.json"), "w") as f:
                    f.write(json.dumps(chat.to_dict(chat_messages, contacts), indent=4))

            # Build the .zip file of the backup data
            archive_out = Path(self.out_file)
            print(f"Creating archive at {archive_out}. This may take a long time.")
            start_time = time.time()
            shutil.make_archive(archive_out.with_suffix(''), "zip", temp_dir)
            print(f"Created {archive_out.stat().st_size / 1e+9:.1f}GB archive in {(time.time() - start_time) / 60:.2f} minutes.")
        except sqlite3.DatabaseError as e:
            if "file is not a database" in str(e):
                print("There was a problem reading the messages. It looks like this iPhone backup may be encrypted — this script requires unencrypted backups.")
            else:
                print(f"There was a problem reading the messages: {e}")
        except KeyboardInterrupt:
            print("Interrupted. Cancelling backup.")
        except Exception as e:
            print(f"Something went wrong while processing the messages: {e}")
        finally:
            # Always delete the temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)


class Message():
    """ Represents a message retrieved from the get_messages.sql query. """

    def __init__(self, id: int, chat_identifier: str, sender: str, is_from_me: int, text: str, date: int, attachment_path: str) -> None:
        self.id = id
        self.chat_identifier = chat_identifier
        self.sender = sender
        self.is_from_me = is_from_me == 1
        self.text = text
        if self.text:
            self.text = self.text.strip()
        self.date = utils.convert_date(date)
        self.attachment_path = attachment_path

    def get_attachment_source(self, in_dir: str) -> Path:
        """ Find the actual path to the attachment in the backup directory. """
        # Apple generates the backup directory structure by SHA1 hashing the path
        domainpath = "MediaDomain-" + self.attachment_path.replace("~/", "")
        filename = sha1(domainpath.encode('utf-8')).hexdigest()

        # The backup directory is organized into subfolders using the first two digits of the hash
        dirname = filename[:2]

        filepath = Path(in_dir, dirname, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"failed to find attachment {self.attachment_path} at {filepath}")

        return filepath

    def get_attachment_dest_filename(self) -> Path:
        """ Find the filename where the attachment will be stored. """
        if self.attachment_path is None:
            return None

        return '-'.join(self.attachment_path.split('/')[-2:])

    def copy_attachment(self, in_dir: str, out_dir: str) -> None:
        """ Copy the actual attachment to the given output directory. """
        if self.attachment_path is not None:
            src = self.get_attachment_source(in_dir)
            dst_name = self.get_attachment_dest_filename()
            shutil.copy2(src, Path(out_dir, dst_name))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "sender": self.sender,
            "is_from_me": self.is_from_me,
            "text": self.text,
            "attachment_path": self.get_attachment_dest_filename()
        }

    @staticmethod
    def row_factory(cursor, row):
        return Message(*row)


class Contact():
    """ Represents a contact retrieved from the get_contacts.sql query. """

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

    def get_full_name(self):
        return f"{self.first_name if self.first_name else ''} {self.last_name if self.last_name else ''}".strip()

    @staticmethod
    def row_factory(cursor, row):
        return Contact(*row)


class Chat():
    """ Represents a chat retrieved from the get_chats.sql query. """

    def __init__(self, id: int, chat_identifier: str, display_name: str, last_message_date: int, participants: str) -> None:
        self.id = id
        self.chat_identifier = chat_identifier
        self.display_name = display_name
        self.last_message_date = utils.convert_date(last_message_date)
        self.participants = participants.split(",")

    def get_participant_names(self, contacts: list[Contact]) -> dict[str, str]:
        """ Get a dictionary mapping a participant identifier (e.g. phone number) to a contact name. """
        names = {}

        for id in self.participants:
            # Try to find the identifier in contacts
            for c in contacts:
                if id in c.identifiers:
                    names[id] = c.get_full_name()
                    break
            
            # If no contact found, just map to the same identifier
            if id not in names:
                names[id] = id

        return names

    def to_dict(self, messages: list[Message], contacts: list[Contact]) -> dict:
        return {
            "chat_id": self.id,
            "chat_identifier": self.chat_identifier,
            "display_name": self.display_name,
            "last_message_date": self.last_message_date,
            "participants": self.get_participant_names(contacts),
            "messages": messages
        }

    @staticmethod
    def row_factory(cursor, row):
        return Chat(*row)
