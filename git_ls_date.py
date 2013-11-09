#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import sys

#=======================================
# config
#=======================================

_name = 'git-ls-date'
_version = '0.0.1'
_license = 'MIT License'
_description = ''
_url = 'https://github.com/ton1517/git-ls-date'
_author = 'ton1517'
_author_email = 'tonton1517@gmail.com'

#=======================================
# git
#=======================================

class GitCommandErrorException(Exception):
    """if git returns error, raise this exception."""

    def __init__(self, command, message):
        self.message = message
        self.command = command

    def __str__(self):
        return self.command + "\n" + self.message

def git(cmd):
    """run git command.
    Return : return command output string
    Raise : GitCommandErrorException
    """

    stdout, stderr = Popen("git " + cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE).communicate()

    if stderr:
        raise GitCommandErrorException(cmd, stderr.decode())

    return stdout.decode()

class Commit(object):

    def __init__(self, date, hash):
        self.date = date
        self.hash = hash

    def __str__(self):
        return "%s %s" % (self.date, self.hash)

class FilesParser(object):
    """FilesParser run 'git ls-files' and parse."""

    def __init__(self, pathes = []):
        self.pathes = pathes if type(pathes) is list else [pathes]

        self.__abbrev_to_full = {}
        self.__full_to_abbrev = {}

        self.files = None
        self.files_full = None

        self.__parse_files()

    def __parse_files(self):
        args = " ".join(["\'%s\'" % f for f in self.pathes])
        self.files = git("ls-files "+args).split("\n")[:-1]
        self.files_full = git("ls-files --full-name "+args).split("\n")[:-1]

        for i, f in enumerate(self.files):
            full = self.files_full[i]
            self.__abbrev_to_full[f] = full
            self.__abbrev_to_full[full] = full
            self.__full_to_abbrev[full] = f
            self.__full_to_abbrev[f] = f

    def get_full(self, file):
        """ return full path.
        Arg : filename
        Return : return full path. if no result, return None.
        """

        return self.__abbrev_to_full.get(file)

    def get_abbrev(self, full_path):
        """ return abbrev path.
        Arg : full path string
        Return : return abbrev path. if no result, return None.
        """

        return self.__full_to_abbrev.get(full_path)

class LogParser(object):
    """LogParser runs 'git log' and parse."""

    log_format = "log --oneline --name-only --no-merges --pretty=format:'%h %ad' --date="

    def __init__(self, files_parser, date_option = None):
        self.files_parser = files_parser
        self.date_option = date_option

        self.commits = []
        self.__commit_contains_file_hash = {}

        self.files_quote = ["\'%s\'"%f for f in self.files_parser.files]
        self.log_format += date_option if date_option else "local"
        self.log_format_no_file += date_option if date_option else "local"

        self.__parse_log()

    def __parse_log(self):
        log_str = git(self.log_format+" "+" ".join(self.files_quote))[:-1].split("\n\n")

        for l in log_str:
            one_commit = l.split("\n")
            date, hash, files = self.__parse_one_commit_contains_filename(one_commit)
            commit = Commit(date, hash)
            self.commits.append(commit)

            for f in files:
                self.__append_commit(f, commit)

    def __append_commit(self, key_file, commit):
        commit_list = self.__commit_contains_file_hash.get(key_file, [])
        commit_list.append(commit)
        self.__commit_contains_file_hash[key_file] = commit_list

    def __parse_one_commit_contains_filename(self, one_commit):
        commit_info = one_commit[0]
        date, hash = self.__parse_one_commit(commit_info)
        files = one_commit[1:]
        return date, hash, files

    def __parse_one_commit(self, one_commit):
        return one_commit[8:], one_commit[:7]

    def get_commits_contains(self, file):
        """return commits that contains file.
        Arg : filename
        Return : commit list
        """

        full_path = self.files_parser.get_full(file)
        commits = self.__commit_contains_file_hash.get(full_path)

        return commits

    def get_first_commit_contains(self, file):
        """return commit that file are changed last.
        Arg : filename
        Return : commit object
        """

        commits = self.get_commits_contains(file)
        return commits[-1] if commits else None

    def get_last_commit_contains(self, file):
        """return commit that file are added first.
        Arg : filename
        Return : commit object
        """

        commits = self.get_commits_contains(file)
        return commits[0] if commits else None

#=======================================
# main
#=======================================

def main():
    pass

if __name__ == "__main__":
    main()

