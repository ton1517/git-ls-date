from setuptools import setup
import git_ls_date

setup(
    name = git_ls_date._name,
    version = git_ls_date._version,
    description = git_ls_date._description,
    long_description = open("README.rst").read(),
    url = git_ls_date._url,
    license = git_ls_date._license,
    author = git_ls_date._author,
    author_email = git_ls_date._author_email,
    py_modules = ['git_ls_date'],
    entry_points = {
        "console_scripts": ["git-ls-date = git_ls_date:main"]
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Utilities',
    ]
)

