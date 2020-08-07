import os
import sys
import dotenv
import yaml
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, List, Tuple, Any
from importlib import import_module
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace


class AppConfigFileNotSet(Exception):
    pass


class AppConfig:

    def __init__(self, **kwargs):
        self._config = kwargs

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value


class RamboConfig:
    root_dir = Path.cwd().absolute()

    def __init__(self, app: Dict[str, str], entrypoint_paths: Dict[str, List], terminal: Dict[str, List[str]], **kwargs) -> None:

        self.app = app
        self.entrypoint_paths = entrypoint_paths
        self.terminal = terminal

        optional_kwargs = ['db_connections', 'environment']

        for optional_kwarg in optional_kwargs:
            try:
                setattr(self, f"_{optional_kwarg}", kwargs[optional_kwarg])
            except KeyError:
                pass

    @property
    def db_connections(self) -> Dict[str, str]:
        return getattr(self, '_db_connections', {})

    @property
    def environment(self) -> Dict[str, str]:
        return getattr(self, '_environment', {})

    @property
    def load_env_file(self) -> bool:
        return True if self.environment.get('load_env_file', '') else False

    @property
    def env_file_name(self) -> str:
        return self.environment.get('env_file_name', '')

    @property
    def app_name(self) -> str:
        return self.app['name']

    @property
    def app_description(self) -> str:
        return self.app.get('description', '')

    @property
    def app_config_file(self) -> str:
        return self.app.get('config_file', '')

    @property
    def verbs(self) -> List[str]:
        return self.terminal['verbs']

    @property
    def nouns(self) -> List[str]:
        return self.terminal['nouns']

    @property
    def verb_noun_map(self) -> List[str]:
        return [f"{verb}_{noun}" for verb in self.verbs for noun in self.nouns]

    def get_formatted_actions(self) -> Dict[Tuple[str], Dict[str, Any]]:
        return {

            ('verb',): {
                'help': 'The action you would like to perform',
                'choices': self.verbs
            },

            ('noun',): {
                'help': 'The element to act upon',
                'choices': self.nouns
            }
        }

    def get_app_config(self) -> AppConfig:
        if self.app_config_file:
            app_config_path = self.root_dir / self.app_config_file
            app_config = yaml.safe_load(app_config_path.open())
            return AppConfig(**app_config)
        else:
            raise AppConfigFileNotSet(f"No app config file is set in rambo.yml. Did you intend to provide one?")

    def get_entrypoint_paths(self) -> List[Path]:
        return [Path(p) for p in self.entrypoint_paths]

    def get_db_connection_string(self, connection_name: str) -> str:

        try:
            env_var = self.db_connections[connection_name]
            return os.environ[env_var]
        except KeyError:
            raise KeyError(f'no database with the name {connection_name} has been configured in rambo.yml')

    @staticmethod
    def parse_config(config_path: Path = None) -> 'RamboConfig':

        if config_path is None:
            config_path = RamboConfig.root_dir / "rambo.yml"

        return RamboConfig(**yaml.safe_load(config_path.open())['rambo'])

    def parse_nouns_and_verbs(self) -> Namespace:
        arg_parser = ArgumentParser()

        for command, options in self.get_formatted_actions().items():
            arg_parser.add_argument(*command, **options)
        return arg_parser.parse_args(sys.argv[1:3])


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

        self.rambo = RamboConfig.parse_config(config_path)

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


def collect_entry_points(config_path: Path = None) -> Dict[str, EntryPoint]:
    """
    function is used to introspect and collect all EntryPoint classes from the paths
    configured in the rambo.yml file.

    Returns: Dict[str, EntryPoint]
        The return dictionary contains all classes which have inherited from EntryPoint,
        with a corresponding name key. This key is used as a verb_noun_mapping.
    """
    config = RamboConfig.parse_config(config_path)
    modules = []
    entry_points = []

    for entry_point_path in config.get_entrypoint_paths():

        doted_path = entry_point_path.as_posix().replace('/', '.')

        # include path if we have an __init__.py file which has been used to create the entry points.
        modules.append(import_module(doted_path))

        for _, name, _ in pkgutil.iter_modules([entry_point_path]):
            module = import_module(f"{doted_path}.{name}")
            modules.append(module)

    """
    look through all the modules that were collected, and if any of the classes found
    in the corresponding module have have inherited from the class EntryPoint, add
    them to the list of callable entry point classes.
    """
    for module in modules:

        for name, obj in inspect.getmembers(module):

            if inspect.isclass(obj):

                try:
                    if obj.is_entry_point():
                        entry_points.append(obj)
                except AttributeError:
                    pass

    return {entry_point.name(): entry_point for entry_point in entry_points}


def run_entry_point(config_path: Path = None):
    """
    function introspects all entry point paths as specified in the rsterm.yml file, and collects all
    objects which have inherited from EntryPoint, and maps them to the verb / noun mappings as specified
    in rambo.yml If a mapping combination exists in the config file, but there is no corresponding class
    name, then a NotImplementedError is raised, and the function prints an error message and exits.
    """
    entry_points = collect_entry_points(config_path)
    config = RamboConfig.parse_config(config_path)
    ns = config.parse_nouns_and_verbs()
    key = f"{ns.verb}_{ns.noun}"
    exit_code = 0

    try:
        if key not in entry_points.keys():
            raise NotImplementedError
        else:
            entry_point = entry_points[key].new(config_path)
            entry_point.run()

    except NotImplementedError:
        print("invalid command. Not yet implemented, try again.")
        exit_code = 1

    exit(exit_code)  # exit no matter what


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

