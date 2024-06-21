from glob import glob
from os import path
from typing import List


def get_all_test_images():
    return __get_test_files("*", "app_input_test_images")


def __get_test_files(files_pattern, *sub_folders) -> List[str]:
    base_path = path.join(path.sep, path.dirname(path.dirname(path.realpath(__file__))), "data", *sub_folders)
    all_files = glob(f"{base_path}/{files_pattern}")
    filtered_files = [file for file in all_files if not file.endswith('.md')]
    return filtered_files
