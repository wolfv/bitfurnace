import os
import re
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, List, Any

class BaseFileTransformer:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.backup_path = filepath.with_suffix(".bak")
        self.transformations: List[Callable[['BaseFileTransformer'], Any]] = []

    def add_transformation(self, transformation: Callable[['BaseFileTransformer'], Any]):
        """Add a transformation function to be applied to the file content."""
        self.transformations.append(transformation)

    def apply_transformations(self):
        """Apply all registered transformations to the file content."""
        with open(self.filepath, 'r') as file:
            content = file.read()

        for transform in self.transformations:
            content = transform(content)

        with open(self.filepath, 'w') as file:
            file.write(content)

    def create_backup(self):
        """Create a backup of the original file."""
        shutil.copy2(self.filepath, self.backup_path)

    def restore_backup(self):
        """Restore the file from the backup."""
        if os.path.exists(self.backup_path):
            shutil.move(self.backup_path, self.filepath)

    def remove_backup(self):
        """Remove the backup file."""
        if os.path.exists(self.backup_path):
            os.remove(self.backup_path)

class MakeFileTransformer:
    def remove_make_var(self, var: str):
        pattern = rf'^{re.escape(var)}[ \t]*[\\?+:!]?=.*\n'
        self.add_transformation(lambda content: re.sub(pattern, '', content, flags=re.MULTILINE))

    def change_make_var(self, var: str, value: str):
        pattern = rf'^({re.escape(var)}[ \t]*[\\?+:!]?=).*'
        repl = rf'\1 {value}'
        self.add_transformation(lambda content: re.sub(pattern, repl, content, flags=re.MULTILINE))

class FileTransformer(BaseFileTransformer, MakeFileTransformer):
    pass

@contextmanager
def Patcher(filepath: str | Path):
    """
    Context manager for safely transforming file content with backup and restore capabilities.
    
    Usage:
    with file_transformer('example.txt') as ft:
        ft.add_transformation(lambda content: content.replace('old', 'new'))
        ft.add_transformation(lambda content: content.upper())
    """
    transformer = FileTransformer(Path(filepath))
    transformer.create_backup()
    try:
        yield transformer
        transformer.apply_transformations()
    except Exception as e:
        transformer.restore_backup()
        raise e
    finally:
        transformer.remove_backup()

# Example usage:
if __name__ == "__main__":
    def replace_hello_with_hi(content: str) -> str:
        return content.replace("Hello", "Hi")

    def make_uppercase(content: str) -> str:
        return content.upper()

    with Patcher(Path("example.txt")) as ft:
        ft.add_transformation(replace_hello_with_hi)
        ft.add_transformation(make_uppercase)
