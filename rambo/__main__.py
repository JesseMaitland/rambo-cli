import subprocess
from rambo import EntryPoint, run_entry_point
from pathlib import Path


class NewProject(EntryPoint):

    entry_point_args = {
        ('project_name', ): {
            'help': "the name of your cli application."
        },

        ('--install', '-i'): {
            'help': 'set if you want to run "pip install -e ." to make your project available on the terminal',
            'action': 'store_true'
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.validate_project_name()

        self.root = Path(__file__).absolute().parent
        self.cwd = Path().cwd().absolute()

        self.rambo_template_path = self.root / "rambo_template.yml"
        self.main_template_path = self.root / "main_template.txt"
        self.setup_template_path = self.root / "setup_template.txt"
        self.rambo_path = self.cwd / "rambo.yml"
        self.setup_path = self.cwd / "setup.py"

        self.project_path = self.cwd / self.cmd_args.project_name
        self.terminal_path = self.project_path / "terminal"
        self.entry_path = self.terminal_path / "entry"

        self.project_init = self.project_path / "__init__.py"
        self.project_main = self.project_path / "__main__.py"
        self.terminal_init = self.terminal_path / "__init__.py"
        self.entry_path_init = self.entry_path / "__init__.py"

    def run(self) -> None:
        self.create_project_dirs()
        self.create_python_files()

        templated_rambo = self.template_rambo(self.rambo_template_path)
        templated_setup = self.template_rambo(self.setup_template_path)
        self.create_rambo_file(templated_rambo)
        self.create_setup_file(templated_setup)
        self.install_local()

        if self.cmd_args.install:
            print(f"rambo project setup complete. try running {self.cmd_args.project_name} on your terminal!")
        else:
            print("rambo project setup complete!")

    def validate_project_name(self):
        disallowed_chars = '!"#$%&\'()*+,./:;<=>?@[\\]^`{|}~'
        for char in self.cmd_args.project_name:
            if char in disallowed_chars:
                raise ValueError(f"The following characters are not allowed in a project name. {disallowed_chars}")

    def create_project_dirs(self):
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.terminal_path.mkdir(parents=True, exist_ok=True)
        self.entry_path.mkdir(parents=True, exist_ok=True)

    def create_python_files(self):
        self.project_init.touch(exist_ok=True)
        self.terminal_init.touch(exist_ok=True)
        self.entry_path_init.touch(exist_ok=True)
        self.project_main.touch(exist_ok=True)
        self.project_main.write_text(self.main_template_path.read_text())

    def template_rambo(self, template_path: Path) -> str:
        content = template_path.read_text()
        return content.format(name=self.cmd_args.project_name)

    def create_rambo_file(self, templated_rambo: str):
        self.rambo_path.touch(exist_ok=True)
        self.rambo_path.write_text(templated_rambo)

    def create_setup_file(self, templated_setup: str):
        self.setup_path.touch(exist_ok=True)
        self.setup_path.write_text(templated_setup)

    def install_local(self):
        if self.cmd_args.install:
            cmd = ['pip', 'install', '-e', '.']
            subprocess.run(cmd)


def main():
    run_entry_point(Path(__file__).absolute().parent / "rambo.yml")



