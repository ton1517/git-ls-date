# -*- coding: utf-8 -*-

import os
from mock import Mock
from nose.tools import *
import git_ls_date

class TestConfiguration(object):

    @raises(SystemExit)
    def test_help1(self):
        config = git_ls_date.Configuration()
        config.argparse(["-h"])

    @raises(SystemExit)
    def test_help2(self):
        config = git_ls_date.Configuration()
        config.argparse(["--help"])

    @raises(SystemExit)
    def test_version1(self):
        config = git_ls_date.Configuration()
        config.argparse(["-v"])

    @raises(SystemExit)
    def test_version2(self):
        config = git_ls_date.Configuration()
        config.argparse(["--version"])

    @raises(SystemExit)
    def test_invalid_option(self):
        config = git_ls_date.Configuration()
        config.argparse(["--bar"])

    def check_date(self, date):
        config = git_ls_date.Configuration()
        config.argparse(["-d", date])
        eq_(config.date, date)

    def test_date(self):
        self.check_date("relative")
        self.check_date("local")
        self.check_date("iso")
        self.check_date("rfc")
        self.check_date("short")
        self.check_date("raw")
        self.check_date("default")

    def test_format(self):
        opt = "{ld} {lh} {fd} {fh} {f}"
        config = git_ls_date.Configuration()
        config.argparse(['--format', opt])
        eq_(config.format, opt)


class TestIgnoreGitConfig(object):

    def setup(self):
        global git_ls_date
        self.__orig_git = git_ls_date.git

        def git_side(cmd):
            if cmd == "config --get-regexp git-ls-date":
                return ""
            else:
                self.__orig_git(cmd)

        git_ls_date.git = Mock(side_effect=git_side)

    def teardown(self):
        global git_ls_date
        git_ls_date.git = self.__orig_git

    def test_date_default(self):
        config = git_ls_date.Configuration()
        config.argparse()

        eq_(config.date, "short")

class TestGitConfig(object):

    def setup(self):
        global git_ls_date
        self.__orig_git = git_ls_date.git

        def git_side(cmd):
            if cmd == "config --get-regexp git-ls-date":
                return "git-ls-date.date relative\n"
            else:
                self.__orig_git(cmd)

        git_ls_date.git = Mock(side_effect=git_side)

    def teardown(self):
        global git_ls_date
        git_ls_date.git = self.__orig_git

    def test_read_gitconfig(self):
        config = git_ls_date.Configuration()
        config.argparse()

        eq_(config.date, "relative")


class TestGitCommandErrorException(object):

    message = "error message"
    git_cmd = "git log"

    def test_GitCommandErrorException(self):
        e = git_ls_date.GitCommandErrorException(self.git_cmd, self.message)

        eq_(str(e), self.git_cmd+"\n"+self.message)

    @raises(git_ls_date.GitCommandErrorException)
    def test_raise_GitCommandErrorException(self):
        e = git_ls_date.GitCommandErrorException(self.git_cmd, self.message)
        raise e

class TestGit(object):

    def test_command(self):
        output = git_ls_date.git("--version")
        ok_("git version" in output)

    @raises(git_ls_date.GitCommandErrorException)
    def test_raise(self):
        git_ls_date.git("hoge")

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

        parser = git_ls_date.FilesParser(path)
        self.check_files(parser, files, files)


    def test_args(self):
        pathes = ["testfiles/testfile1", "testfiles/testfile2"]
        files = ["testfiles/testfile1", "testfiles/testfile2"]

        parser = git_ls_date.FilesParser(pathes)
        self.check_files(parser, files, files)

    def test_no_arg(self):
        files = [".gitignore", ".python-version", "LICENSE", "MANIFEST.in", "README.rst", "git_ls_date.py", "setup.py", "test_git_ls_date.py", "testfiles/testdirectory/testfile4", "testfiles/testfile1", "testfiles/testfile2", "testfiles/testfile3", "tox.ini"]

        parser = git_ls_date.FilesParser()
        self.check_files(parser, files, files)

    def test_under_directory(self):
        os.chdir("./testfiles/")
        files = ["testfile1", "testfile2", "testfile3", "testdirectory/testfile4"]
        files_full = ["testfiles/testfile1", "testfiles/testfile2", "testfiles/testfile3", "testfiles/testdirectory/testfile4"]

        parser = git_ls_date.FilesParser()
        self.check_files(parser, files, files_full)

    def test_wrong_path(self):
        wrong_file = "hoge"
        parser = git_ls_date.FilesParser(wrong_file)

        eq_(parser.files, [])
        eq_(parser.files_full, [])

        eq_(parser.get_full(wrong_file), None)
        eq_(parser.get_abbrev(wrong_file), None)

class TestLogParser(object):

    def setup(self):

        # create FilesParser Mock

        pathes = ["testfiles"]
        files = ["testfile1", "testfile2", "testfile3", "testdirectory/testfile4"]
        files_full = ["testfiles/testfile1", "testfiles/testfile2", "testfiles/testfile3", "testfiles/testdirectory/testfile4"]

        abbrev_to_full_dict = {
                "testfile1":"testfiles/testfile1",
                "testfile2":"testfiles/testfile2",
                "testfile3":"testfiles/testfile3",
                "testdirectory/testfile4":"testfiles/testdirectory/testfile4",
                "testfiles/testfile1":"testfiles/testfile1",
                "testfiles/testfile2":"testfiles/testfile2",
                "testfiles/testfile3":"testfiles/testfile3",
                "testfiles/testdirectory/testfile4":"testfiles/testdirectory/testfile4"
        }

        full_to_abbrev_dict = {
                "testfile1":"testfile1",
                "testfile2":"tetfile2",
                "testfile3":"testfile3",
                "testdirectory/testfile4":"testdirectory/testfile4",
                "testfiles/testfile1":"testfile1",
                "testfiles/testfile2":"testfile2",
                "testfiles/testfile3":"testfile3",
                "testfiles/testdirectory/testfile4":"testdirectory/testfile4"
        }

        def get_full(file):
            return abbrev_to_full_dict.get(file)

        def get_abbrev(file):
            return full_to_abbrev_dict.get(file)

        self.files_parser_mock = Mock()
        self.files_parser_mock.pathes = pathes
        self.files_parser_mock.files = files
        self.files_parser_mock.files_full = files_full

        get_full_mock = Mock()
        get_full_mock.side_effect = get_full
        self.files_parser_mock.get_full = get_full_mock

        get_abbrev_mock = Mock()
        get_abbrev_mock.side_effect = get_abbrev
        self.files_parser_mock.get_abbrev = get_abbrev_mock

        # create commit mocks

        self.correct_commits_raw = [
            self.create_commit_mock("b9720cf", "1383998635 +0900"),
            self.create_commit_mock("d8cd0a2", "1383991898 +0900"),
            self.create_commit_mock("0adbbd6", "1383977357 +0900"),
            self.create_commit_mock("b14e272", "1383977226 +0900"),
            self.create_commit_mock("e5fa5ad", "1383976796 +0900"),
            self.create_commit_mock("da5e0fa", "1383975672 +0900"),
            self.create_commit_mock("586fb9d", "1383975617 +0900")
        ]

        self.correct_commits_iso = [
            self.create_commit_mock("b9720cf", "2013-11-09 21:03:55 +0900"),
            self.create_commit_mock("d8cd0a2", "2013-11-09 19:11:38 +0900"),
            self.create_commit_mock("0adbbd6", "2013-11-09 15:09:17 +0900"),
            self.create_commit_mock("b14e272", "2013-11-09 15:07:06 +0900"),
            self.create_commit_mock("e5fa5ad", "2013-11-09 14:59:56 +0900"),
            self.create_commit_mock("da5e0fa", "2013-11-09 14:41:12 +0900"),
            self.create_commit_mock("586fb9d", "2013-11-09 14:40:17 +0900")
        ]

    def create_commit_mock(self, hash, date):
        commit = Mock()
        commit.date = date
        commit.hash = hash
        return commit

    def eq_commit(self, correct_commit, commit):
        eq_(correct_commit.hash, commit.hash)
        eq_(correct_commit.date, commit.date)

    def test_commits(self):
        log_parser = git_ls_date.LogParser(self.files_parser_mock, "raw")

        eq_(len(self.correct_commits_raw), len(log_parser.commits))

        for i, commit in enumerate(log_parser.commits):
            self.eq_commit(self.correct_commits_raw[i], commit)

        log_parser = git_ls_date.LogParser(self.files_parser_mock, "iso")
        eq_(len(self.correct_commits_iso), len(log_parser.commits))

        for i, commit in enumerate(log_parser.commits):
            self.eq_commit(self.correct_commits_iso[i], commit)

    def test_contains(self):
        commits = self.correct_commits_raw

        file_commits_hash = {
                "testfile1": [commits[0], commits[2], commits[6]],
                "testfile2": [commits[1], commits[5]],
                "testfile3": [commits[1], commits[4]],
                "testdirectory/testfile4": [commits[3]]
            }

        log_parser = git_ls_date.LogParser(self.files_parser_mock, "raw")

        for file in file_commits_hash.keys():
            correct_commits = file_commits_hash[file]
            commits = log_parser.get_commits_contains(file)

            eq_(len(correct_commits), len(commits))

            for i, commit in enumerate(commits):
                correct_commit = correct_commits[i]
                self.eq_commit(correct_commit, commit)

            self.eq_commit(correct_commits[0], log_parser.get_last_commit_contains(file))
            self.eq_commit(correct_commits[-1], log_parser.get_first_commit_contains(file))

    def test_not_contains(self):
        log_parser = git_ls_date.LogParser(self.files_parser_mock, "raw")

        eq_(None, log_parser.get_commits_contains("hoge"))
        eq_(None, log_parser.get_first_commit_contains("hoge"))
        eq_(None, log_parser.get_last_commit_contains("hoge"))


    @raises(git_ls_date.GitCommandErrorException)
    def test_date_option_error(self):
        log_parser = git_ls_date.LogParser(self.files_parser_mock, "hoge")

