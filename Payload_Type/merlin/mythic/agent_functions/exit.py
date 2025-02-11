
from merlin import MerlinJob
from mythic_payloadtype_container.MythicCommandBase import *
import json


class ExitArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ExitCommand(CommandBase):
    cmd = "exit"
    needs_admin = False
    help_cmd = "exit"
    description = "Instruct the agent to quit running and exit"
    version = 1
    supported_ui_features = ["callback_table:exit"]
    author = "@Ne0nd0g"
    argument_class = ExitArguments
    attackmapping = []

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        # Merlin jobs.Command message type
        command = {
            "command": self.cmd,
        }

        task.args.add_arg("type", MerlinJob.CONTROL, ParameterType.Number)
        task.args.add_arg("payload", json.dumps(command), ParameterType.String)
        return task

    async def process_response(self, response: AgentResponse):
        pass
