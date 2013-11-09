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
        return "%s %s " % (self.date, self.hash)

class FilesParser(object):
    """FilesParser run 'git ls-files' and parse."""

    def __init__(self, pathes = []):
        self.pathes = pathes if type(pathes) is list else [pathes]

        args = " ".join(["\'%s\'" % f for f in self.pathes])
        self.files = git("ls-files "+args).split("\n")[:-1]
        self.files_full = git("ls-files --full-name "+args).split("\n")[:-1]

        self.__abbrev_to_full = {}
        self.__full_to_abbrev = {}

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

#=======================================
# main
#=======================================

def main():
    pass

if __name__ == "__main__":
    main()

