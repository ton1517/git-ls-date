#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2013 ton1517 <tonton1517@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""git-ls-date

Usage:
  git ls-date [--date=<option>] [--format=<format>] [<path>]...
  git ls-date -h | --help
  git ls-date -v | --version

Options:
  -h --help                                             Show help.
  -v --version                                          Show version.
  -d --date=(relative|local|default|iso|rfc|short|raw)  Date option.(default: short)
  -f --format=<format>                                  Show-format option. See SHOW FORMAT.(default: "{fd} {fh}  {ld} {lh}  {f}")

SHOW FORMAT:

  --format option allows you to specify which information you want to show.

  placeholders:

    * {ld}: last commit date
    * {fd}: first commit date
    * {lh}: last commit hash
    * {fh}: first commit hash
    * {f}:  filename

See https://github.com/ton1517/git-ls-date
"""

from subprocess import Popen, PIPE
import sys
import getopt
import re

#=======================================
# config
#=======================================

_name = 'git-ls-date'
_version = '0.1.1'
_license = 'MIT License'
_description = 'git-ls-date is git sub command shows first and last commit date.'
_url = 'https://github.com/ton1517/git-ls-date'
_author = 'ton1517'
_author_email = 'tonton1517@gmail.com'

def help():
    version()
    print("\n%s\n%s\nby %s <%s>\n" % (_description, _url, _author, _author_email))
    usage()

def usage():
    print(__doc__)

def version():
    print("%s %s" % (_name, _version))

class Configuration(object):
    """parse comannd option and set configuration."""

    shortopts = "hvd:f:"
    longopts = ["help", "version", "date=", "format="]

    date_default = "short"
    format_default =  "{fd} {fh}  {ld} {lh}  {f}"

    def __init__(self):
        self.paths = None
        self.date = None
        self.__config_hash = {}

        self.__read_gitconfig()

        self.date = self.__config_hash.get("date", self.date_default)
        self.format = self.__config_hash.get("format",self.format_default)

    def __read_gitconfig(self):
        config_lines = git("config --get-regexp " + _name).split("\n")[:-1]

        config_re = re.compile("%s\.(.*?) (.*)" % _name)
        for line in config_lines:
            result = config_re.search(line)
            self.__config_hash[result.group(1)] = result.group(2)

    def argparse(self, args = []):
        """parse commandline arguments.
        Arg : commandline arguments. you should exclude commandline name.
                for example 'configuration.argparse(sys.argv[1:])'
        """
        try:
            opts, args = getopt.getopt(args, self.shortopts, self.longopts)
        except getopt.GetoptError as e:
            usage()
            sys.exit(1)

        self.pathes = args

        for opt, value in opts:
            value = value.strip()

            if opt == "--help" or opt == "-h":
                help()
                sys.exit()
            elif opt == "--version" or opt == "-v":
                version()
                sys.exit()
            elif opt == "--date" or opt == "-d":
                self.date = value
            elif opt == "--format" or opt == "-f":
                self.format = value
                try:
                    self.format.format(ld="",fd="",lh="",fh="",f="")
                except (KeyError, ValueError) as e:
                    print("Invalid format error.")
                    print(e)
                    sys.exit(1)

            else:
                usage()
                sys.exit(1)

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

    log_format = "log --oneline --name-only --author-date-order -c --pretty=format:'%h %ad' --date="

    def __init__(self, files_parser, date_option = None):
        self.files_parser = files_parser
        self.date_option = date_option

        self.commits = []
        self.__commit_contains_file_hash = {}

        self.files_quote = ["\'%s\'"%f for f in self.files_parser.files]
        self.log_format += date_option if date_option else "local"

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
        Return : commit list. if file has no commit, return None.
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

    try:
        config = Configuration()
        config.argparse(sys.argv[1:])

        files_parser = FilesParser(config.pathes)
        parser = LogParser(files_parser, config.date)
    except GitCommandErrorException as e:
        print(e)
        sys.exit(1)

    for f in files_parser.files:
        fc = parser.get_first_commit_contains(f)
        lc = parser.get_last_commit_contains(f)
        formatted_info = config.format.format(fd=fc.date, fh=fc.hash, ld=lc.date, lh=lc.hash, f=f)
        print(formatted_info)

if __name__ == "__main__":
    main()

