# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import logging
import pathlib
import time

import pytest

from axonius_api_client.constants import LOG_LEVEL_CONSOLE
from axonius_api_client.constants import LOG_LEVEL_FILE
from axonius_api_client.constants import LOG_NAME_FILE
from axonius_api_client.constants import LOG_NAME_STDERR
from axonius_api_client.constants import LOG_NAME_STDOUT
from axonius_api_client.exceptions import ToolsError
from axonius_api_client.logs import add_file
from axonius_api_client.logs import add_null
from axonius_api_client.logs import add_stderr
from axonius_api_client.logs import add_stdout
from axonius_api_client.logs import del_file
from axonius_api_client.logs import del_null
from axonius_api_client.logs import del_stderr
from axonius_api_client.logs import del_stdout
from axonius_api_client.logs import get_obj_log
from axonius_api_client.logs import gmtime
from axonius_api_client.logs import localtime
from axonius_api_client.logs import LOG
from axonius_api_client.logs import str_level


class TestLogs:
    """Test logs."""

    def test_gmtime(self):
        gmtime()
        assert logging.Formatter.converter == time.gmtime

    def test_localtime(self):
        localtime()
        assert logging.Formatter.converter == time.localtime

    def test_get_obj_log(self):
        log = get_obj_log(obj=self, level="warning")
        assert log.name == "axonius_api_client.tests.tests_pkg.test_logs.TestLogs"
        assert log.level == logging.WARNING

    def test_str_level_int(self):
        assert str_level(level=10) == "DEBUG"

    def test_str_level_str_int(self):
        assert str_level(level="10") == "DEBUG"

    def test_str_level_str(self):
        assert str_level(level="debug") == "DEBUG"

    def test_str_level_fail(self):
        with pytest.raises(ToolsError):
            str_level(level="xx")

    def test_add_del_stderr(self):
        h = add_stderr(obj=LOG)
        assert h.name == LOG_NAME_STDERR
        assert str_level(level=h.level).lower() == LOG_LEVEL_CONSOLE
        assert isinstance(h, logging.StreamHandler)
        assert h in LOG.handlers

        dh = del_stderr(obj=LOG)
        assert isinstance(dh, dict)
        assert LOG.name in dh
        assert isinstance(dh[LOG.name], list)
        assert h in dh[LOG.name]
        assert h not in LOG.handlers

    def test_add_del_stdout(self):
        h = add_stdout(obj=LOG)
        assert h.name == LOG_NAME_STDOUT
        assert str_level(level=h.level).lower() == LOG_LEVEL_CONSOLE
        assert isinstance(h, logging.StreamHandler)
        assert h in LOG.handlers

        dh = del_stdout(obj=LOG)
        assert isinstance(dh, dict)
        assert LOG.name in dh
        assert isinstance(dh[LOG.name], list)
        assert h in dh[LOG.name]
        assert h not in LOG.handlers

    def test_add_del_null(self):
        del_null(obj=LOG)
        h = add_null(obj=LOG)
        assert h.name == "NULL"
        assert isinstance(h, logging.NullHandler)
        assert h in LOG.handlers

        fh = add_null(obj=LOG)
        assert fh is None

        dh = del_null(obj=LOG)

        assert isinstance(dh, dict)
        assert isinstance(dh[LOG.name], list)

        assert LOG.name in dh
        f = dh.pop(LOG.name)

        assert h in f
        assert h not in LOG.handlers

    def test_add_del_file(self):
        h = add_file(obj=LOG)
        assert h.name == LOG_NAME_FILE
        assert str_level(level=h.level).lower() == LOG_LEVEL_FILE
        assert isinstance(h, logging.handlers.RotatingFileHandler)
        assert h in LOG.handlers
        assert getattr(h, "PATH", None)
        assert isinstance(h.PATH, pathlib.Path)

        dh = del_file(LOG)
        assert isinstance(dh, dict)
        assert LOG.name in dh
        assert isinstance(dh[LOG.name], list)
        assert h in dh[LOG.name]
        assert h not in LOG.handlers
