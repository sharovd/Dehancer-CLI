from __future__ import annotations

from os import path
from pathlib import Path


def get_all_test_images() -> list[str]:
    return __get_test_files("*", "app_input_test_images")


def __get_test_files(files_pattern: str, *sub_folders: str) -> list[str]:
    base_path = path.join(path.sep, Path(Path(path.realpath(__file__)).parent).parent, "data", *sub_folders)
    all_files = Path(base_path).glob(files_pattern)
    return [str(file) for file in all_files if file.suffix != ".md"]
