import pkgutil
import inspect
from typing import Dict
from importlib import import_module
from rambo.entrypoint import (
    BaseEntryPoint,
    SingleActionEntryPoint,
    MultiActionEntryPoint,
    parse_cmd_args
)


def collect_entry_points(module_name: str) -> Dict[str, BaseEntryPoint]:
    entrypoints = []
    for _, name, _ in pkgutil.iter_modules(path=[f"{module_name}/entrypoints"]):

        module = import_module(name=f"{module_name}.entrypoints.{name}")

        for mod_name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if issubclass(obj, BaseEntryPoint):
                    if obj != SingleActionEntryPoint and obj != MultiActionEntryPoint:
                        entrypoints.append(obj)
    return {entrypoint.name(): entrypoint for entrypoint in entrypoints}


def run_entrypoint(module_name: str) -> None:
    entrypoints = collect_entry_points(module_name)
    commands = ""
    for key, value in entrypoints.items():
        commands = commands + '\n -> ' + key + value.description

    main_command = {
        ('command',): {
            'help': f"The available commands are\n{commands}\n"
        }
    }

    # the first arg always maps to an entrypoint class
    command_ns = parse_cmd_args(main_command, 1, 2)
    entrypoint = entrypoints[command_ns.command]

    if issubclass(entrypoint, SingleActionEntryPoint):
        entrypoint().action()
        exit()

    elif issubclass(entrypoint, MultiActionEntryPoint):
        action_command = {
            ('action',): {
                'help': entrypoint.help()
            }
        }
        action_ns = parse_cmd_args(action_command, 2, 3)
        entrypoint().execute(action_ns.action)
        exit()

    else:
        raise NotImplementedError("the command was not able to be discovered. Something is broken!")
