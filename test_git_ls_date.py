# -*- coding: utf-8 -*-

import os
from nose.tools import *
from git_ls_date import *

class TestGitCommandErrorException(object):

    message = "error message"
    git_cmd = "git log"

    def test_GitCommandErrorException(self):
        e = GitCommandErrorException(self.git_cmd, self.message)

        eq_(str(e), self.git_cmd+"\n"+self.message)

    @raises(GitCommandErrorException)
    def test_raise_GitCommandErrorException(self):
        e = GitCommandErrorException(self.git_cmd, self.message)
        raise e

class TestGit(object):

    def test_command(self):
        output = git("--version")
        ok_("git version" in output)

    @raises(GitCommandErrorException)
    def test_raise(self):
        git("hoge")

class TestFilesParser(object):

    def check_files(self, parser, correct_files, correct_files_full):
        correct_files_sorted = sorted(correct_files)
        result_files_sorted = sorted(parser.files)
        eq_(correct_files_sorted, result_files_sorted)

        correct_files_full_sorted = sorted(correct_files_full)
        result_files_full_sorted = sorted(parser.files_full)
        eq_(correct_files_full_sorted, result_files_full_sorted)

        for i, file in enumerate(correct_files):
            f = parser.get_full(file)
            eq_(f, correct_files_full[i])
            f = parser.get_abbrev(file)
            eq_(f, file)

        for i, file in enumerate(correct_files_full):
            f = parser.get_full(file)
            eq_(f, file)
            f = parser.get_abbrev(file)
            eq_(f, correct_files[i])


    def test_one_arg(self):
        path = "testfiles"
        files = ["testfiles/testfile1", "testfiles/testfile2", "testfiles/testfile3", "testfiles/testdirectory/testfile4"]
        files.sort()

        parser = FilesParser(path)
        self.check_files(parser, files, files)


    def test_args(self):
        pathes = ["testfiles/testfile1", "testfiles/testfile2"]
        files = ["testfiles/testfile1", "testfiles/testfile2"]

        parser = FilesParser(pathes)
        self.check_files(parser, files, files)

    def test_no_arg(self):
        files = [".gitignore", ".python-version", "LICENSE", "README.rst", "git_ls_date.py", "setup.py", "test_git_ls_date.py", "testfiles/testdirectory/testfile4", "testfiles/testfile1", "testfiles/testfile2", "testfiles/testfile3", "tox.ini"]

        parser = FilesParser()
        self.check_files(parser, files, files)

    def test_under_directory(self):
        os.chdir("./testfiles/")
        files = ["testfile1", "testfile2", "testfile3", "testdirectory/testfile4"]
        files_full = ["testfiles/testfile1", "testfiles/testfile2", "testfiles/testfile3", "testfiles/testdirectory/testfile4"]

        parser = FilesParser()
        self.check_files(parser, files, files_full)

    def test_wrong_path(self):
        wrong_file = "hoge"
        parser = FilesParser(wrong_file)

        eq_(parser.files, [])
        eq_(parser.files_full, [])

        eq_(parser.get_full(wrong_file), None)
        eq_(parser.get_abbrev(wrong_file), None)

