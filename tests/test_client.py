import pytest
from cortex.client import upload_sample


def test_upload_sample():
    assert upload_sample('127.0.0.1', 8000, '/home/room/workspace/AdvancedSystemDesign/cortex/data/sample.mind.gz') == 0
