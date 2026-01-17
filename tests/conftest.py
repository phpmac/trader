#!/usr/bin/env python3
"""
pytest 配置
"""

import pytest


# 配置 pytest-asyncio
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    """配置 asyncio mode"""
    config.addinivalue_line("markers", "asyncio: mark test as async")
