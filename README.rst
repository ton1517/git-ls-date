git-ls-date
===========
git-ls-date is git sub command shows first and last commit date.

Examples
========

Basic
------
default option is

- date = short
- format = "{fd} {fh}  {ld} {lh}  {f}"

::

    $ git ls-date
    2013-11-05 7ab1b16  2013-11-05 7ab1b16  README.rst
    2013-11-07 342ad26  2013-11-10 2826492  git_ls_date.py

How long ago?
------------------
::

    git ls-date --date relative --format "first commit is {fd: <20} | {f}"
    first commit is 6 days ago           | .gitignore
    first commit is 3 days ago           | .python-version
    first commit is 3 days ago           | LICENSE
    first commit is 77 minutes ago       | MANIFEST.in
    first commit is 6 days ago           | README.rst
    first commit is 3 days ago           | git_ls_date.py
    first commit is 3 days ago           | setup.py
    first commit is 3 days ago           | test_git_ls_date.py
    first commit is 30 hours ago         | testfiles/testdirectory/testfile4
    first commit is 30 hours ago         | testfiles/testfile1
    first commit is 30 hours ago         | testfiles/testfile2
    first commit is 30 hours ago         | testfiles/testfile3
    first commit is 3 days ago           | tox.ini

Only show commit hash
----------------------
::

    $ git ls-date --format="{lh} {f}
    7ab1b16 README.rst
    2826492 git_ls_date.py

Sort files by last commit date
-------------------------------
::

    $ git ls-date --date iso --format "{ld} {f}" | sort
    2013-11-05 04:40:11 +0900 .gitignore
    2013-11-05 04:40:11 +0900 README.rst
    2013-11-07 23:22:29 +0900 setup.py
    2013-11-07 23:34:59 +0900 LICENSE
    2013-11-08 15:36:16 +0900 .python-version
    2013-11-09 15:07:06 +0900 testfiles/testdirectory/testfile4
    2013-11-09 19:11:38 +0900 testfiles/testfile2
    2013-11-09 19:11:38 +0900 testfiles/testfile3
    2013-11-09 21:03:55 +0900 testfiles/testfile1
    2013-11-09 22:22:38 +0900 tox.ini
    2013-11-10 15:32:19 +0900 test_git_ls_date.py
    2013-11-10 18:28:24 +0900 git_ls_date.py
    2013-11-10 19:45:40 +0900 MANIFEST.in

Installation
============

Install from pypi
-----------------
::

    easy_install git-ls-date

or

::

    pip install git-ls-date

Install from github
-------------------
::

    git clone https://github.com/ton1517/git-ls-date.git
    cd git-ls-date
    python setup.py install

Manual setup
------------
1. Copy git_ls_date.py to a directory that is in your PATH.
2. Rename it to git-ls-date.
3. Change it to executable.

::

    cd ~/bin
    wget https://raw.github.com/ton1517/git-ls-date/master/git_ls_date.py -O git-ls-date
    chmod +x git-ls-date

Usage
=====
Usage:
    ::

      git ls-date [--date=<option>] [--format=<format>] [<path>]...
      git ls-date -h | --help
      git ls-date -v | --version

Options:
    ::

      -h --help                                             Show help.
      -v --version                                          Show version.
      -d --date=(relative|local|default|iso|rfc|short|raw)  Date option.(default: short)
      -f --format=<format>                                  Show-format option. See SHOW FORMAT.(default: "{fd} {fh}  {ld} {lh}  {f}")

SHOW FORMAT:
    format option allows you to specify which information you want to show.

    placeholders:
        * {ld}: last commit date
        * {fd}: first commit date
        * {lh}: last commit hash
        * {fh}: first commit hash
        * {f}:  filename

    for example:
        ::

            $ git ls-date --date=local --format="{fd} {fh}  {ld} {lh}  {f}" ./README.rst
            Tue Nov 5 04:40:11 2013 7ab1b16  Tue Nov 5 04:40:11 2013 7ab1b16  README.rst

    You can see more format spec to http://docs.python.org/3/library/string.html?highlight=string.format#formatspec

Gitconfig
=========
You can write option in .gitconfig

for example:
    ::

        [git-ls-date]
            date = relative
            format = {lh} {ld: <25} {f}

    ::

        $ git ls-date
        7ab1b16 6 days ago                  README.rst
        2826492 2 hours ago                 git_ls_date.py

