import unittest
from unittest import mock
from pathlib import Path
from backup_tool import BackupTool, Message, Contact


def get_test_backup_path() -> str:
    return Path(Path(__file__).parent, "testdata", "test_backup").resolve()


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.msg = Message(1, "test title", "test id", "+11111111111,+11111111111", "+11111111111", 0, " test text ",
                           501787857000000000, "~/Library/SMS/Attachments/64/04/A06F2E76-B277-4429-A4F7-61F7FE60D2ED/ms-G5Go5i.gif")

    def test_build(self):
        self.assertEqual(self.msg.participants, [
                         "+11111111111", "+11111111111"])
        self.assertEqual(self.msg.is_from_me, False)
        self.assertEqual(self.msg.text, "test text")
        self.assertEqual(self.msg.date, 1480095057)

    def test_get_attachment_source_success(self):
        self.assertEqual(self.msg.get_attachment_source(get_test_backup_path()), Path(
            get_test_backup_path(), "d5", "d53ceee6ab358ae7013bbfc83b472e5c9f04e713"))

    def test_get_attachment_source_fail(self):
        self.msg.attachment_path = "~/Library/SMS/Attachments/64/04/A06F2E76-B277-4429-A4F7-61F7FE60D2ED/ms-G5Go5i.jpg"
        self.assertRaises(
            FileNotFoundError, self.msg.get_attachment_source, get_test_backup_path())

    @mock.patch("backup_tool.shutil")
    def test_copy_attachment_success(self, mock_shutil):
        src = self.msg.get_attachment_source(get_test_backup_path())
        dst = Path("test", "output",
                   "A06F2E76-B277-4429-A4F7-61F7FE60D2ED-ms-G5Go5i.gif")

        self.msg.copy_attachment(
            get_test_backup_path(), Path("test", "output"))
        mock_shutil.copy2.assert_called_with(src, dst)


class TestContact(unittest.TestCase):
    def test_build(self):
        contact = Contact(
            1, "John", "Smith", "+11111111111,(222) 222-2222,333-333-3333,+1 444 444 4444,+1 (555) 555 5555,(666)6666666,johnsmith@gmail.com")
        self.assertEqual(contact.identifiers, ["+11111111111", "+12222222222", "+13333333333",
                         "+14444444444", "+15555555555", "+16666666666", "johnsmith@gmail.com"])


class TestBackupTool(unittest.TestCase):
    def setUp(self):
        self.tool = BackupTool(get_test_backup_path(), "out")

    def get_mock_open(self) -> mock.MagicMock:
        """
        Patch the open() function so messages.json and contacts.json aren't created.
        Still return the correct values for our .sql files.
        """

        files = {}

        get_messages_sql_path = Path(
            Path(__file__).parent, "sql", "get_messages.sql").resolve()
        with open(get_messages_sql_path, 'r') as f:
            files[get_messages_sql_path] = f.read()

        get_contacts_sql_path = Path(
            Path(__file__).parent, "sql", "get_contacts.sql").resolve()
        with open(get_contacts_sql_path, 'r') as f:
            files[get_contacts_sql_path] = f.read()

        def open_mock(path, *args, **kwargs):
            for expected_path, content in files.items():
                if path == expected_path:
                    return mock.mock_open(read_data=content).return_value
                elif args[0] == "w":
                    return mock.mock_open(read_data="").return_value
            raise FileNotFoundError(
                f"mocked.open() was called with {path} but has no behavior defined for it")

        return mock.MagicMock(side_effect=open_mock)

    def test_get_messages(self):
        messages = self.tool._get_messages()
        self.assertEqual(messages, [
            Message(24341, "Family Chat", "chat36260175973343405", "+11111111111,+11111111112,+11111111113,+11111111114,+11111111115",
                    "+11111111114", 0, "Test message 1", 501787857000000000, "~/Library/SMS/Attachments/64/04/A06F2E76-B277-4429-A4F7-61F7FE60D2ED/ms-G5Go5i.gif"),
            Message(24342, "Family Chat", "chat36260175973343405", "+11111111111,+11111111112,+11111111113,+11111111114,+11111111115",
                    "+11111111111", 0, "Test message 2", 501811998000000000, None),
            Message(24343, "Family Chat", "chat36260175973343405", "+11111111111,+11111111112,+11111111113,+11111111114,+11111111115",
                    "+11111111113", 0, "Test message 3", 501823640000000000, None),
            Message(24344, "Brother Chat", "chat45372165166753", "+11111111111,+11111111114",
                    "+11111111111", 0, "Test message 4", 501967237000000000, None),
            Message(24345, "Brother Chat", "chat45372165166753", "+11111111111,+11111111114",
                    None, 1, "Test message 5", 501967624000000000, None)
        ])

    def test_get_contacts(self):
        contacts = self.tool._get_contacts()
        self.assertEqual(contacts, [
            Contact(1, "Dad", None, "+1 (111) 111-1111,+12222222222,dad@gmail.com"),
            Contact(3, "Mom", None, "4444444444"),
            Contact(4, "John", "Smith", "3333333333")
        ])

    @mock.patch("backup_tool.shutil")
    @mock.patch("backup_tool.os")
    @mock.patch("backup_tool.tempfile")
    @mock.patch.object(Message, "copy_attachment")
    def test_run(self, mock_msg_copy, mock_tempfile, mock_os, mock_shutil):
        out_dir = Path("User", "AppData", "Temp")
        mock_tempfile.mkdtemp.return_value = out_dir

        with mock.patch("builtins.open", self.get_mock_open()):
            self.tool.run()

        mock_tempfile.mkdtemp.assert_called_once()
        mock_os.mkdir.assert_called_once_with(Path(out_dir, "attachments"))
        mock_msg_copy.assert_called_once_with(get_test_backup_path(), Path(out_dir, "attachments"))
        mock_shutil.make_archive.assert_called_once_with(
            Path("out"), "zip", out_dir)


if __name__ == "__main__":
    unittest.main()
