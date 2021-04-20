import pytest
import shutil


@pytest.fixture(autouse=True, scope='session')
def test_suite_cleanup_thing():
    yield

    build = "./new_tests/build/"
    print("Cleaning up tests.")

    shutil.rmtree(build)
