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

