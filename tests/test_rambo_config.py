import yaml
from tests import FIXTURE_PATH
from unittest import TestCase
from rambo.configs import RamboConfig


config_path = FIXTURE_PATH / "test_rambo_config.yml"


class TestRamboConfig(TestCase):

    def setUp(self) -> None:

        with config_path.open() as config_file:
            raw_config = yaml.safe_load(config_file)['rambo']
            self.rambo_config = RamboConfig(**raw_config)

    def test_app_name(self):
        self.assertTrue(self.rambo_config.app_name == 'first_blood')

    def test_app_description(self):
        self.assertTrue(self.rambo_config.app_description == 'spam, beans, eggs')

    def test_pip_package(self):
        self.assertTrue(self.rambo_config.is_pip_package is True)

    def test_rambo_parse_config(self):
        parsed_config = RamboConfig.parse_config(config_path)
        self.assertEqual(parsed_config.db_connections, self.rambo_config.db_connections)
        self.assertEqual(parsed_config.app_name, self.rambo_config.app_name)
        self.assertEqual(parsed_config.app_description, self.rambo_config.app_description)
        self.assertEqual(parsed_config.load_env_file, self.rambo_config.load_env_file)
        self.assertEqual(parsed_config.env_file_name, self.rambo_config.env_file_name)

