import sys
import os
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install

VERSION = '0.0.1'


def readme():
    with open('README.md') as file:
        return file.read()


def post_install():
    py_inter_path = Path(sys.executable)
    py_version = f"python{sys.version_info[0]}.{sys.version_info[0]}"
    path_to_install = py_inter_path.parent.parent / "lib" / py_version / "site-packages" / "rambo"
    rambo_config_file_path = path_to_install / "rambo.yml"
    rambo_config_content = rambo_config_file_path.read_text().format(entry=path_to_install)
    rambo_config_file_path.write_text(rambo_config_content)


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(tag, VERSION)
            sys.exit(info)


class Install(install):

    def run(self):
        install.run(self)




setup(
    name='rambo',
    version=VERSION,
    author='Jesse Maitland',
    discription='A simple toolkit for making a cli',
    include_package_data=True,
    long_description=readme(),
    install_requires=[
        'python-dotenv',
        'pyyaml'
    ],
    license='MIT',
    packages=find_packages(exclude=('tests*', 'venv')),
    entry_points={
        'console_scripts': ['rambo = rambo.__main__:main']
    },
    download_url="",
    long_description_content_type="text/markdown",
    python_requires='>=3',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
