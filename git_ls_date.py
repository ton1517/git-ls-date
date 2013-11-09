#!/usr/bin/env python

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

#=======================================
# main
#=======================================

def main():
    pass

if __name__ == "__main__":
    main()

