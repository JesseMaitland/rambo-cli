import sys
import dotenv
from typing import Dict, Tuple, Any
from abc import ABC, abstractmethod
from pathlib import Path
from argparse import ArgumentParser, Namespace
from rambo.configs.rambo_config import RamboConfig


class EntryPoint(ABC):
    """
    Base class to be used by all program entry points. If specific arguments are to be used for the
    inheriting child class, then the entry_point_args dictionary can be overridden with the format
    below

    entry_point_args = {
        ('arg or --flag', None or -f): {
            'ArgumentParser kwargs': 'ArgumentParser values'
        }
    }

    """
    entry_point_args = {}

    def __init__(self, config_path: Path = None):

        self.rambo: RamboConfig = RamboConfig.parse_config(config_path)

        self.cmd_args: Namespace = self.parse_entry_flags(self.entry_point_args)

        if self.rambo.load_env_file:
            self.env_file_path = Path().cwd() / self.rambo.env_file_name
            self.load_app_env(self.env_file_path)
        else:
            self.env_file_path = None

    @classmethod
    def new(cls, config_path: Path = None):
        cls._validate_class_name()
        return cls(config_path)

    @abstractmethod
    def run(self) -> None:
        pass

    @classmethod
    def name(cls) -> str:
        name = cls.__name__
        snake = ''.join([f'_{c.lower()}' if c.isupper() else c for c in name])
        return snake.lstrip('_')

    @classmethod
    def _validate_class_name(cls) -> None:
        underscores = 0
        for char in cls.name():
            if char == '_':
                underscores += 1

        if underscores > 1:
            raise Exception("Class names must consists of 2 words, in the format VerbNoun.")

    @classmethod
    def is_entry_point(cls) -> bool:
        return False if cls.__name__ == 'EntryPoint' else True

    @staticmethod
    def parse_entry_flags(args_config: Dict) -> Namespace:
        arg_parser = ArgumentParser()

        for command, options in args_config.items():
            arg_parser.add_argument(*command, **options)
        return arg_parser.parse_args(sys.argv[3:])

    @staticmethod
    def load_app_env(env_file_path: Path):
        if not env_file_path.exists():
            raise FileNotFoundError(f"no .env file found at {env_file_path.as_posix()}")
        else:
            dotenv.load_dotenv(env_file_path)


def parse_cmd_args(args_config: Dict[Tuple, Dict[str, Any]]) -> Namespace:
    """
    Parse command line args in one call, using a dict as a configuration.
    Args:
        args_config: Dict[Tuple, Dict[str, Any]] according to standard lib ArgumentParser kwargs

    Returns: Namespace
    """
    arg_parser = ArgumentParser()

    for command, options in args_config.items():
        arg_parser.add_argument(*command, **options)
    return arg_parser.parse_args()
