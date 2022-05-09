import unittest
import utils
from pathlib import Path

class TestUtils(unittest.TestCase):
    def test_convert_date(self):
        self.assertEqual(utils.convert_date(673633712174999936), 1651940912)
        self.assertEqual(utils.convert_date(502317225), 1480624425)

    def test_get_archive_format(self):
        self.assertEqual(utils.get_archive_format(Path("temp", "dir", "output.zip")), "zip")
        self.assertEqual(utils.get_archive_format(Path("temp", "dir", "output.tar.gz")), "gztar")

if __name__ == "__main__":
    unittest.main()
