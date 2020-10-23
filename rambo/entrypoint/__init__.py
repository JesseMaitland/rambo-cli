import sys
from textwrap import dedent
from typing import Dict, Tuple, List
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter


def parse_cmd_args(args_config: Dict[Tuple[str, str], Dict[str, str]], arg_index: int = 0,
                   arg_stop_index: int = None) -> Namespace:
    """
    Parse command line args in one call, using a dict as a configuration.
    Args:
        args_config: Dict[Tuple, Dict[str, Any]] according to standard lib ArgumentParser kwargs
        arg_index:   int starting index of the arguments to be parsed from sys.argv
        arg_stop_index: where in the list of sys.argv to stop parsing
    Returns: Namespace
    """
    arg_parser = ArgumentParser(formatter_class=RawTextHelpFormatter)

    for command, options in args_config.items():
        arg_parser.add_argument(*command, **options)

    if arg_stop_index:
        return arg_parser.parse_args(sys.argv[arg_index:arg_stop_index])
    else:
        return arg_parser.parse_args(sys.argv[arg_index:])


class BaseEntryPoint:
    """
    Base class to be used by all program entry points.

    If a method with the name 'action' is defined, it is assumed that the entrypoint only has a single action and this method
    will me called by the entrypoint runner. This allows for arguments like

    ```
        my-app action
    ```

    If more than one action is desired, than define your methods with the prefix "action" for example

    ```
    def action_new(self):
        # do things here
    ```

    this will allow an invocation like below, where the value of action 2 will be mapped automatically to the method
    `action_new()` in the entrypoint class `Project`

    ```
        my-app project new
    ```

    If specific arguments are to be used for the
    inheriting child class, then the entry_point_args dictionary can be overridden with the format
    below

    entry_point_args = {
        ('arg or --flag', None or -f): {
            'ArgumentParser kwargs': 'ArgumentParser values'
        }
    }

    """

    # override this class dict with any arguments which apply only to this entry point
    # or which would otherwise apply to all descendant EntryPoint objects.
    discover = False
    entry_point_args = {}
    description = ""
    help_text = ""

    @classmethod
    def name(cls) -> str:
        """
        Returns: str the name of this class in snake case
        """
        name = cls.__name__
        snake = ''.join([f'_{c.lower()}' if c.isupper() else c for c in name])
        return snake.lstrip('_')

    @classmethod
    def get_actions(cls) -> List[str]:
        return [a.replace('action', '').replace('_', '') for a in cls.__dict__.keys() if a.startswith('action')]

    @classmethod
    def help(cls) -> str:
        help_msg = f'available actions for command {cls.name()}\n'
        for action in cls.get_actions():
            help_msg = help_msg + '-> ' + action + '\n'

        help_msg = help_msg + dedent(f"""
        {cls.help_text}
        """)
        return help_msg


class SingleActionEntryPoint(BaseEntryPoint):

    def __init__(self):
        self.args: Namespace = parse_cmd_args(self.entry_point_args, arg_index=2)
        super().__init__()

    def action(self) -> None:
        raise NotImplementedError("a single action entrypoint must override the base action method.")


class MultiActionEntryPoint(BaseEntryPoint):

    def __init__(self):
        self.args: Namespace = parse_cmd_args(self.entry_point_args, arg_index=3)
        super().__init__()

    def execute(self, action_name: str) -> None:

        try:
            action = getattr(self, f"action_{action_name}")

        except AttributeError:
            print(f"{action_name} is not a valid action for object {self.name()}")
            print(f"For object {self.name()} the actions are {self.get_actions()}")
            exit()

        else:
            action()
