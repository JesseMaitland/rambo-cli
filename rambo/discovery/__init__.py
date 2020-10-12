import pkgutil
import inspect
from typing import Dict
from importlib import import_module
from rambo.entrypoint import EntryPoint, parse_cmd_args


def collect_entry_points(module_name: str) -> Dict[str, EntryPoint]:

    entrypoints = []
    for _, name, _ in pkgutil.iter_modules(path=[f"{module_name}/entrypoints"]):

        module = import_module(name=f"{module_name}.entrypoints.{name}")

        for mod_name, obj in inspect.getmembers(module):

            if inspect.isclass(obj) and issubclass(obj, EntryPoint):
                entrypoints.append(obj)
    return {entrypoint.name(): entrypoint for entrypoint in entrypoints}


def run_entrypoint(module_name: str) -> None:

    entrypoints = collect_entry_points(module_name)

    main_command = {
        ('command',): {
            'help': f"available commands are {list(entrypoints.keys())}"
        }
    }

    action_command = {
        ('action',): {
            'help': "here we do an action"
        }
    }
    # the first arg always maps to an entrypoint class
    command_ns = parse_cmd_args(main_command, 1, 2)
    entrypoint = entrypoints[command_ns.command]

    if getattr(entrypoint, 'action', None):
        entrypoint().action()
    else:
        action_ns = parse_cmd_args(action_command, 2, 3)
        entrypoint().execute(action_ns.action)
