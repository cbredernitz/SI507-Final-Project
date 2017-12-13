import unittest
from Reddit_Analysis import *

class Testing_Import_files(unittest.TestCase):
    def test_import_files(self):
        self.assertNotEqual(len(CLIENT_ID), 0, "Make sure to fill in client_id on file called reddit_secret")
