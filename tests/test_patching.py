from bitfurnace.patch import Patcher
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

class _TestDataContainer:
    def __init__(self, path: Path):
        self.temp_dir = TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / path

    def get(self, filename: str) -> Path:
        # copy the file to the temporary directory
        shutil.copy2(self.path / filename, self.temp_dir.name)
        return Path(self.temp_dir.name) / filename

@pytest.fixture
def test_data() -> Path:
    return _TestDataContainer(Path(__file__).parent / "data")

def test_patching(test_data):
    test_file = test_data.get("config.mk.in")

    with Patcher(test_file) as ft:
        ft.remove_make_var("CC")

    result = test_file.read_text()
    assert "CC = cc" not in result

    with Patcher(test_file) as ft:
        ft.change_make_var("TIFFLIB", "-ltiff")
        ft.change_make_var("JPEGLIB", "-ljpeg")
    
    result = test_file.read_text()
    assert "TIFFLIB = -ltiff" in result
    assert "JPEGLIB = -ljpeg" in result