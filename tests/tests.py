from unittest import mock
from unittest import TestCase
import unittest
from zoom_dl import zoomdl
import os
import sys
import random
import string


class ConfirmTest(TestCase):
    @mock.patch('zoom_dl.zoomdl.input', create=True)
    def test_confirm_yes(self, mocked_input):
        mocked_input.side_effect = ["y"]
        result = zoomdl.confirm("Anything")
        self.assertEqual(result, True)

    @mock.patch('zoom_dl.zoomdl.input', create=True)
    def test_confirm_no(self, mocked_input):
        mocked_input.side_effect = ["n"]
        result = zoomdl.confirm("Anything")
        self.assertEqual(result, False)

    @mock.patch('zoom_dl.zoomdl.input', create=True)
    def test_confirm_empty(self, mocked_input):
        mocked_input.side_effect = [""]
        result = zoomdl.confirm("Anything")
        self.assertEqual(result, False)

    @mock.patch('zoom_dl.zoomdl.input', create=True)
    def test_confirm_garbage_yes(self, mocked_input):
        mocked_input.side_effect = [
            "fisj", "jfsje", "12", "None", "12.4", "43es", "y"]
        result = zoomdl.confirm("Anything")
        self.assertEqual(result, True)

    @mock.patch('zoom_dl.zoomdl.input', create=True)
    def test_confirm_garbage_no(self, mocked_input):
        mocked_input.side_effect = ["firdhif", "fiufh", "ihfsiuh", "niufsheu", "n"]
        result = zoomdl.confirm("Anything")
        self.assertEqual(result, False)


class FilepathTest(TestCase):
    def test_relative_basic(self):
        cwd = os.getcwd()
        user_fname = "myownrecording"
        ext = "mp4"
        filepath = zoomdl.get_filepath(user_fname=user_fname,
                                       file_fname=None,
                                       extension=ext)
        self.assertEqual(filepath, "{}/{}.{}".format(cwd, user_fname, ext))
    
    def test_relative_both_names(self):
        cwd = os.getcwd()
        user_fname = "myownrecording2"
        ext = "webm"
        filepath = zoomdl.get_filepath(user_fname=user_fname,
                                       file_fname="\\/Absolute/Garbadge",
                                       extension=ext)
        self.assertEqual(filepath, "{}/{}.{}".format(cwd, user_fname, ext))
        


if __name__ == "__main__":
    unittest.main()
