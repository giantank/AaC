import os
#import pytest
from parameterized import parameterized
from unittest import TestCase
from aac.in_out.paths import sanitize_filesystem_path

WORKING_TEST_DIR = os.getcwd()

def _get_working_directory_parent_directory(level_of_directories_up: int = 1) -> str:
    """Get the n-level parent directory from the WORKING_TEST_DIR. Useful for testing '../' in paths."""
    path_to_return = WORKING_TEST_DIR
    for i in range(0, level_of_directories_up):
        new_path = os.path.dirname(path_to_return)
        if new_path != path_to_return:
            path_to_return = new_path
        else:
            break

    return path_to_return

class TestPaths(TestCase):
    @parameterized.expand([
            [f"{WORKING_TEST_DIR}/src/aac/test.py",                     f"{WORKING_TEST_DIR}/src/aac/test.py",],
            [f"{WORKING_TEST_DIR}/../src/aac/test.py",                  f"{os.path.dirname(WORKING_TEST_DIR)}/src/aac/test.py"],
            ["src/aac/test.py",                                         f"{WORKING_TEST_DIR}/src/aac/test.py"],
            ["../../src/aac/test.py",                                   f"{_get_working_directory_parent_directory(2)}/src/aac/test.py"],
            [f"{WORKING_TEST_DIR}/../../src/aac/test.py",               f"{_get_working_directory_parent_directory(2)}/src/aac/test.py"],
            [f"{WORKING_TEST_DIR}/src/aac/test.exe%00.py",              f"{WORKING_TEST_DIR}/src/aac/test.exe.py"],
            [f"{WORKING_TEST_DIR}/%2e%2e%2f/src/aac/test.py",           f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
            [f"{WORKING_TEST_DIR}/%2e%2e//src/aac/test.py",             f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
            [f"{WORKING_TEST_DIR}/..%2f/src/aac/test.py",               f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
            [f"{WORKING_TEST_DIR}/%2e%2e%5c/src/aac/test.py",           f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
            [f"{WORKING_TEST_DIR}/%2e%2e\/src/aac/test.py",             f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
            [f"{WORKING_TEST_DIR}/..%5c\/src/aac/test.py",              f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
            [f"{WORKING_TEST_DIR}/%252e%252e%255c\/src/aac/test.py",    f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
            [f"{WORKING_TEST_DIR}/..%255c\/src/aac/test.py",            f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
            # [f"{WORKING_TEST_DIR}/src/aac/AAA.py",                      f"{WORKING_TEST_DIR}/src/aac/BBB.py"],
        ])
    def test_sequence(self, test_path, expected_result):
            # if test_path == f"{WORKING_TEST_DIR}/src/aac/AAA.py":
            #     pytest.xfail("This test is expected to fail")
            self.assertEqual(sanitize_filesystem_path(test_path),expected_result)

# Works but pytest and unittest don't have == number of tests
# @pytest.mark.parametrize("test_input,expected",[
#     (f"{WORKING_TEST_DIR}/src/aac/test.py",                     f"{WORKING_TEST_DIR}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/../src/aac/test.py",                  f"{os.path.dirname(WORKING_TEST_DIR)}/src/aac/test.py"),
#     ("src/aac/test.py",                                         f"{WORKING_TEST_DIR}/src/aac/test.py"),
#     ("../../src/aac/test.py",                                   f"{_get_working_directory_parent_directory(2)}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/../../src/aac/test.py",               f"{_get_working_directory_parent_directory(2)}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/src/aac/test.exe%00.py",              f"{WORKING_TEST_DIR}/src/aac/test.exe.py"),
#     (f"{WORKING_TEST_DIR}/%2e%2e%2f/src/aac/test.py",           f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/%2e%2e//src/aac/test.py",             f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/..%2f/src/aac/test.py",               f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/%2e%2e%5c/src/aac/test.py",           f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/%2e%2e\/src/aac/test.py",             f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/..%5c\/src/aac/test.py",              f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/%252e%252e%255c\/src/aac/test.py",    f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"),
#     (f"{WORKING_TEST_DIR}/..%255c\/src/aac/test.py",            f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"),
#     pytest.param(f"{WORKING_TEST_DIR}/src/aac/AAA.py",          f"{WORKING_TEST_DIR}/src/aac/BBB.py", marks=pytest.mark.xfail) #this test is expected to fail and will show as an 'xfailed'
#     ])

# def test_sanitize_filesystem_path(test_input, expected):
#     assert sanitize_filesystem_path(test_input) == expected
