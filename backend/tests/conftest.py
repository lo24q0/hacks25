import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


@pytest.fixture
def anyio_backend():
    """
    配置anyio后端为asyncio
    
    Returns:
        str: 后端名称
    """
    return 'asyncio'
