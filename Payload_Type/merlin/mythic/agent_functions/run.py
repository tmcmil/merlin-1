
from merlin import MerlinJob
from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json

# Set to enable debug output to Mythic
debug = False


class RunArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "arguments": CommandParameter(
                name="arguments",
                type=ParameterType.String,
                description="Arguments to start the executable with",
                ui_position=1,
                required=False,
            ),
            "executable": CommandParameter(
                name="executable",
                type=ParameterType.String,
                description="The executable program to start",
                value="whoami",
                ui_position=0,
                required=True,
            ),
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == '{':
                self.load_args_from_json_string(self.command_line)
            else:
                args = str.split(self.command_line)
                self.add_arg("executable", args[0])
                self.add_arg("arguments", " ".join(args[1:]))


class RunCommand(CommandBase):
    cmd = "run"
    needs_admin = False
    help_cmd = "run"
    description = "Run the executable with the provided arguments and return the results"
    version = 1
    author = "@Ne0nd0g"
    argument_class = RunArguments
    attackmapping = ["T1106"]

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = f'{task.args.get_arg("executable")} {task.args.get_arg("arguments")}'

        # Executable Arguments
        args = []
        # TODO Handle argument parsing when quotes and escapes are used
        arguments = task.args.get_arg("arguments").split()
        if len(arguments) == 1:
            args.append(arguments[0])
        elif len(arguments) > 1:
            for arg in arguments:
                args.append(arg)

        # Merlin jobs.Command message type
        command = {
            "command": task.args.get_arg("executable"),
            "args": args,
        }

        task.args.add_arg("type", MerlinJob.CMD, ParameterType.Number)
        task.args.add_arg("payload", json.dumps(command), ParameterType.String)
        task.args.remove_arg("executable")
        task.args.remove_arg("arguments")

        if debug:
            await MythicRPC().execute("create_output", task_id=task.id, output=f'[DEBUG]Returned task:\r\n{task}\r\n')

        return task

    async def process_response(self, response: AgentResponse):
        pass
