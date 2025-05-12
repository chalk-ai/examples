import pytest
from chalk.client import ChalkClient


@pytest.fixture(scope="session")
def client():
    # OPTION 2
    # chalk apply --branch <new branch name>
    # CHALK_CLIENT_ID
    # CHALK_CLIENT_SECRET
    return ChalkClient(branch=True)
