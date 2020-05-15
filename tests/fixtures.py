import os
import pytest

OWD = os.getcwd()


@pytest.fixture(scope="session")
def restore_wd():
    yield os.getcwd()
    print(f"restoring workingdir {OWD}")
    os.chdir(OWD)
