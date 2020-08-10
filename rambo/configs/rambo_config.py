import os
import sys
import yaml
from argparse import ArgumentParser, Namespace
from typing import Dict, List, Tuple, Any
from pathlib import Path
from rambo.exceptions import AppConfigFileNotSet
from rambo.configs.app_config import AppConfig


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
    def is_pip_package(self) -> bool:
        return self.app.get('is_pip_package', False)

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
