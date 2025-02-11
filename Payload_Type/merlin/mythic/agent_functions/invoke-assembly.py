
from merlin import MerlinJob
from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json

# Set to enable debug output to Mythic
debug = False


class InvokeAssemblyArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="assembly",
                cli_name="assembly",
                display_name=".NET Assembly",
                type=ParameterType.String,
                description="Name of the previously loaded assembly to execute",
                parameter_group_info=[ParameterGroupInfo(
                    group_name="Default",
                    ui_position=0,
                    required=True,
                )],
            ),
            CommandParameter(
                name="arguments",
                cli_name="args",
                display_name=".NET Assembly Arguments",
                type=ParameterType.String,
                description="Arguments to invoke (execute) the assembly",
                parameter_group_info=[ParameterGroupInfo(
                    group_name="Default",
                    ui_position=1,
                    required=False,
                )],
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == '{':
                self.load_args_from_json_string(self.command_line)
            else:
                args = str.split(self.command_line)
                if len(args) > 0:
                    self.add_arg("assembly", args[0])
                if len(args) > 1:
                    self.add_arg("arguments", " ".join(args[1:]))


class LoadAssemblyCommand(CommandBase):
    cmd = "invoke-assembly"
    needs_admin = False
    help_cmd = "invoke-assembly"
    description = "Invoke (execute) a .NET assembly that was previously loaded into the Agent's process using the" \
                  " load-assembly command. Use the list-assemblies command to view loaded assemblies"
    version = 1
    author = "@Ne0nd0g"
    argument_class = InvokeAssemblyArguments
    attackmapping = []
    attributes = CommandAttributes(
        spawn_and_injectable=False,
        supported_os=[SupportedOS.Windows]
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = f'{task.args.get_arg("assembly")} {task.args.get_arg("arguments")}'

        # 1. Assembly Name
        # 2. Arguments
        args = [
            self.cmd,
            task.args.get_arg("assembly"),
        ]

        arguments = task.args.get_arg("arguments").split()
        if len(arguments) == 1:
            args.append(arguments[0])
        elif len(arguments) > 1:
            for arg in arguments:
                args.append(arg)

        # Merlin jobs.Command message type
        command = {
            "command": "clr",
            "args": args,
        }

        task.args.add_arg("type", MerlinJob.MODULE, ParameterType.Number)
        task.args.add_arg("payload", json.dumps(command), ParameterType.String)
        task.args.remove_arg("assembly")
        task.args.remove_arg("arguments")

        if debug:
            await MythicRPC().execute("create_output", task_id=task.id, output=f'[DEBUG]Returned task:\r\n{task}\r\n')

        return task

    async def process_response(self, response: AgentResponse):
        pass
