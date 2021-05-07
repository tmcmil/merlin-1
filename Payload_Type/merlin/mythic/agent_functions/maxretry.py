from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicResponseRPC import *
import json

# Set to enable debug output to Mythic
debug = False


class RetryArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "maxretry": CommandParameter(
                name="maxretry",
                type=ParameterType.String,
                description="The maximum amount of times the Agent can fail to check in before it quits running",
                value="7",
                required=True,
            ),
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == '{':
                self.load_args_from_json_string(self.command_line)
            else:
                self.add_arg("maxretry", str.split(self.command_line)[0])


class RetryCommand(CommandBase):
    cmd = "maxretry"
    needs_admin = False
    help_cmd = "maxretry"
    description = "The maximum amount of time the Agent can fail to check in before it quits running"
    version = 1
    author = "@Ne0nd0g"
    argument_class = RetryArguments
    attackmapping = []

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        # Merlin jobs.CONTROL
        task.args.add_arg("type", 11, ParameterType.Number)

        # Merlin jobs.Command message type
        command = {
            "command": self.cmd,
            "args": [task.args.get_arg("maxretry")],
        }

        task.display_params = f'{task.args.get_arg("maxretry")}'

        task.args.add_arg("payload", json.dumps(command), ParameterType.String)
        task.args.remove_arg("maxretry")

        if debug:
            await MythicResponseRPC(task).user_output(f'[DEBUG]Returned task:\r\n{task}\r\n')

        return task

    async def process_response(self, response: AgentResponse):
        pass
