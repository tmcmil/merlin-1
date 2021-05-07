
from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicResponseRPC import *
import json


# Set to enable debug output to Mythic
debug = False


class CreateProcessArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "shellcode": CommandParameter(
                name="shellcode",
                type=ParameterType.File,
                description="The shellcode file you want to execute in the spawnto process",
                ui_position=0,
                required=True,
            ),
            "spawnto": CommandParameter(
                name="spawnto",
                type=ParameterType.String,
                description="The child process that will be started to execute the shellcode in",
                default_value="C:\\Windows\\System32\\WerFault.exe",
                ui_position=1,
                required=True
            ),
            "spawntoargs": CommandParameter(
                name="spawnto arguments",
                type=ParameterType.String,
                description="argument to create the spawnto process with, if any",
                ui_position=2,
                required=False,
            ),
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == '{':
                self.load_args_from_json_string(self.command_line)


class CreateProcessCommand(CommandBase):
    cmd = "create-process"
    needs_admin = False
    help_cmd = "create-process"
    description = "Uses process hollowing to create a child process from the spawnto argument, allocate the provided " \
                  "shellcode into it, execute it, and use anonymous pipes to collect STDOUT/STDERR"
    version = 1
    author = "@Ne0nd0g"
    argument_class = CreateProcessArguments
    attackmapping = ["T1055"]
    attributes = CommandAttributes(
        spawn_and_injectable=False,
        supported_os=[SupportedOS.Windows]
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        # Merlin jobs.MODULE
        task.args.add_arg("type", 16, ParameterType.Number)

        # 1. Shellcode
        # 2. SpawnTo Executable
        # 3. SpawnTo Arguments
        args = [
            base64.b64encode(task.args.get_arg("shellcode")).decode("utf-8"),
            task.args.get_arg("spawnto"),
            task.args.get_arg("spawntoargs")
        ]

        # Merlin jobs.Command message type
        command = {
            "command": "createprocess",
            "args": args,
        }

        task.display_params = f'{json.loads(task.original_params)["shellcode"]}' \
                              f'\nShellcode size: {len(args[0])}\n' \
                              f'spawnto: {task.args.get_arg("spawnto")} ' \
                              f'{task.args.get_arg("spawntoargs")}'

        task.args.add_arg("payload", json.dumps(command), ParameterType.String)
        task.args.remove_arg("shellcode")
        task.args.remove_arg("spawnto")
        task.args.remove_arg("spawntoargs")

        if debug:
            await MythicResponseRPC(task).user_output(f'[DEBUG]Returned task:\r\n{task}\r\n')

        return task

    async def process_response(self, response: AgentResponse):
        pass
