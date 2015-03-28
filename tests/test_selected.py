import re

from datetime import datetime
from tasklib.task import local_zone
from tests.base import IntegrationTest
from time import sleep


class TestAnnotateAction(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.command(
            "TaskWikiAnnotate This is annotation.",
            regex="Task \"test task 1\" annotated.$",
            lines=1)

        self.tasks[0].refresh()
        annotation = self.tasks[0]['annotations']
        assert annotation != []
        assert annotation[0]['description'] == "This is annotation."


class TestAnnotateActionMoved(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.type('2gg')  # Go to the second line
        self.command(
            "TaskWikiAnnotate This is annotation.",
            regex="Task \"test task 2\" annotated.$",
            lines=1)

        self.tasks[1].refresh()
        annotation = self.tasks[1]['annotations']
        assert annotation != []
        assert annotation[0]['description'] == "This is annotation."


class TestAnnotateActionRange(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.type('V2gg')  # Go to the second line
        self.client.feedkeys(":TaskWikiAnnotate This is annotation.")
        self.client.type('<Enter>')

        sleep(2)

        for task in self.tasks:
            task.refresh()

        annotation = self.tasks[0]['annotations']
        assert annotation != []
        assert annotation[0]['description'] == "This is annotation."

        annotation = self.tasks[1]['annotations']
        assert annotation != []
        assert annotation[0]['description'] == "This is annotation."


class TestDeleteAction(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    vimoutput = """
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.command(
            "TaskWikiDelete",
            regex="Task \"test task 1\" deleted.$",
            lines=1)

        for task in self.tasks:
            task.refresh()

        assert self.tasks[0]['status'] == "deleted"
        assert self.tasks[1]['status'] == "pending"


class TestDeleteActionMoved(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    vimoutput = """
    * [ ] test task 1  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.type('2gg')
        self.command(
            "TaskWikiDelete",
            regex="Task \"test task 2\" deleted.$",
            lines=1)
        sleep(1)

        for task in self.tasks:
            task.refresh()

        assert self.tasks[1]['status'] == "deleted"
        assert self.tasks[0]['status'] == "pending"


class TestDeleteActionRange(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    vimoutput = """
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.normal('1gg')
        sleep(1)
        self.client.normal('VG')
        sleep(1)
        self.client.feedkeys(":TaskWikiDelete")
        self.client.type('<Enter>')
        sleep(1)

        for task in self.tasks:
            task.refresh()

        assert self.tasks[1]['status'] == "deleted"
        assert self.tasks[0]['status'] == "deleted"


class TestInfoAction(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.command("TaskWikiInfo")

        assert self.command(":py print vim.current.buffer", silent=False).startswith("<buffer info")
        output = '\n'.join(self.read_buffer())

        header = r'\s*'.join(['Name', 'Value'])
        data = r'\s*'.join(['Description', 'test task 1'])
        data2 = r'\s*'.join(['Status', 'Pending'])

        assert re.search(header, output, re.MULTILINE)
        assert re.search(data, output, re.MULTILINE)
        assert re.search(data2, output, re.MULTILINE)



class TestInfoActionMoved(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.type('2gg')  # Go to the second line
        self.command("TaskWikiInfo")

        assert self.command(":py print vim.current.buffer", silent=False).startswith("<buffer info")
        output = '\n'.join(self.read_buffer())

        header = r'\s*'.join(['Name', 'Value'])
        data = r'\s*'.join(['Description', 'test task 2'])
        data2 = r'\s*'.join(['Status', 'Pending'])

        assert re.search(header, output, re.MULTILINE)
        assert re.search(data, output, re.MULTILINE)
        assert re.search(data2, output, re.MULTILINE)


class TestInfoActionRange(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.type('V2gg')  # Go to the second line
        self.client.feedkeys(":TaskWikiInfo")
        self.client.type('<Enter>')

        sleep(1)

        assert self.command(":py print vim.current.buffer", silent=False).startswith("<buffer info")
        output = '\n'.join(self.read_buffer())

        header = r'\s*'.join(['Name', 'Value'])
        data = r'\s*'.join(['Description', 'test task 1'])
        data2 = r'\s*'.join(['Status', 'Pending'])

        assert re.search(header, output, re.MULTILINE)
        assert re.search(data, output, re.MULTILINE)
        assert re.search(data2, output, re.MULTILINE)


class TestLinkAction(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.command(
            "TaskWikiLink",
            regex="Task \"test task 1\" linked.$",
            lines=1)

        backlink = "wiki: {0}".format(self.filepath)

        self.tasks[0].refresh()
        annotation = self.tasks[0]['annotations']
        assert annotation != []
        assert annotation[0]['description'] == backlink


class TestLinkActionMoved(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.type('2gg')  # Go to the second line
        self.command(
            "TaskWikiLink",
            regex="Task \"test task 2\" linked.$",
            lines=1)

        backlink = "wiki: {0}".format(self.filepath)

        self.tasks[1].refresh()
        annotation = self.tasks[1]['annotations']
        assert annotation != []
        assert annotation[0]['description'] == backlink


class TestLinkActionRange(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.type('V2gg')  # Go to the second line
        self.client.feedkeys(":TaskWikiLink")
        self.client.type('<Enter>')

        backlink = "wiki: {0}".format(self.filepath)

        sleep(2)

        for task in self.tasks:
            task.refresh()

        annotation = self.tasks[0]['annotations']
        assert annotation != []
        assert annotation[0]['description'] == backlink

        annotation = self.tasks[1]['annotations']
        assert annotation != []
        assert annotation[0]['description'] == backlink


class TestStartAction(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    vimoutput = """
    * [S] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.command(
            "TaskWikiStart",
            regex="Task \"test task 1\" started.$",
            lines=1)

        for task in self.tasks:
            task.refresh()

        now = local_zone.localize(datetime.now())

        assert self.tasks[0]['status'] == "pending"
        assert self.tasks[1]['status'] == "pending"

        assert (now - self.tasks[0]['start']).total_seconds() < 5
        assert (self.tasks[0]['start'] - now).total_seconds() < 5

        assert self.tasks[1]['start'] == None


class TestStartActionMoved(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    vimoutput = """
    * [ ] test task 1  #{uuid}
    * [S] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.type('2gg')
        self.command(
            "TaskWikiStart",
            regex="Task \"test task 2\" started.$",
            lines=1)
        sleep(1)

        for task in self.tasks:
            task.refresh()

        now = local_zone.localize(datetime.now())

        assert self.tasks[0]['status'] == "pending"
        assert self.tasks[1]['status'] == "pending"

        assert (now - self.tasks[1]['start']).total_seconds() < 5
        assert (self.tasks[1]['start'] - now).total_seconds() < 5

        assert self.tasks[0]['start'] == None


class TestStartActionRange(IntegrationTest):

    viminput = """
    * [ ] test task 1  #{uuid}
    * [ ] test task 2  #{uuid}
    """

    vimoutput = """
    * [S] test task 1  #{uuid}
    * [S] test task 2  #{uuid}
    """

    tasks = [
        dict(description="test task 1"),
        dict(description="test task 2"),
    ]

    def execute(self):
        self.client.normal('1gg')
        sleep(1)
        self.client.normal('VG')
        sleep(1)
        self.client.feedkeys(":TaskWikiStart")
        self.client.type('<Enter>')
        sleep(1)

        for task in self.tasks:
            task.refresh()

        now = local_zone.localize(datetime.now())

        assert self.tasks[0]['status'] == "pending"
        assert self.tasks[1]['status'] == "pending"

        assert (now - self.tasks[0]['start']).total_seconds() < 5
        assert (self.tasks[0]['start'] - now).total_seconds() < 5

        assert (now - self.tasks[1]['start']).total_seconds() < 5
        assert (self.tasks[1]['start'] - now).total_seconds() < 5
