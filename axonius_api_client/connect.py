# -*- coding: utf-8 -*-
"""Easy all-in-one connection handler."""
import logging
import pathlib
import re
from typing import List, Optional, Union

import requests

from .api import Adapters, Dashboard, Devices, Enforcements, Instances, RunAction, System, Users
from .auth import ApiKey
from .constants import (
    LOG_FILE_MAX_FILES,
    LOG_FILE_MAX_MB,
    LOG_FILE_NAME,
    LOG_FILE_PATH,
    LOG_FMT_BRIEF,
    LOG_FMT_VERBOSE,
    LOG_LEVEL_API,
    LOG_LEVEL_AUTH,
    LOG_LEVEL_CONSOLE,
    LOG_LEVEL_FILE,
    LOG_LEVEL_HTTP,
    LOG_LEVEL_PACKAGE,
    TIMEOUT_CONNECT,
    TIMEOUT_RESPONSE,
)
from .exceptions import ConnectError, InvalidCredentials
from .http import Http
from .logs import LOG, add_file, add_stderr, get_obj_log, set_log_level
from .tools import json_dump, sysinfo
from .version import __version__ as VERSION


class Connect:
    """Easy all-in-one connection handler for using the API client.

    Examples:
        >>> import os
        >>>
        >>> import axonius_api_client as axonapi  # noqa: F401
        >>> from axonius_api_client.connect import Connect
        >>> from axonius_api_client.constants import load_dotenv
        >>>
        >>> # read the API key, API secret, and URL from a ".env" file
        >>> load_dotenv()
        >>> AX_URL = os.environ["AX_URL"]
        >>> AX_KEY = os.environ["AX_KEY"]
        >>> AX_SECRET = os.environ["AX_SECRET"]
        >>>
        >>> # create a client using the url, key, and secret
        >>> client = Connect(url=AX_URL, key=AX_KEY, secret=AX_SECRET)
        >>>
        >>> # start the client, will perform login to URL using key & secret
        >>> client.start()
        >>>
        >>> # work with device assets
        >>> devices = client.devices
        >>>
        >>> # work with user assets
        >>> users = client.users
        >>>
        >>> # work with adapters and adapter connections
        >>> adapters = client.adapters
        >>>
        >>> # work with enforcements
        >>> enforcements = client.enforcements
        >>>
        >>> # work with users, roles, global settings, and more
        >>> system = client.system
        >>>
        >>> # work with instances
        >>> instances = client.instances
        >>>
        >>> # work with dashboards and discovery cycles
        >>> dashboard = client.dashboard

    """

    REASON_RES: List[str] = [
        re.compile(r".*?object at.*?\>\: ([a-zA-Z0-9\]\[: ]+)"),
        re.compile(r".*?\] (.*) "),
    ]
    """patterns to look for in exceptions that we can pretty up for user display."""

    def start(self):
        """Connect to and authenticate with Axonius."""
        if not self.STARTED:
            sysinfo_dump = json_dump(sysinfo())
            LOG.debug(f"SYSTEM INFO: {sysinfo_dump}")

            try:
                self.AUTH.login()
            except Exception as exc:
                if not self.WRAPERROR:
                    raise

                pre = f"Unable to connect to {self.HTTP.url!r}"

                if isinstance(exc, requests.ConnectTimeout):
                    timeout = self.HTTP.CONNECT_TIMEOUT
                    msg = f"{pre}: connection timed out after {timeout} seconds"
                    cnxexc = ConnectError(msg)
                elif isinstance(exc, requests.ConnectionError):
                    reason = self._get_exc_reason(exc=exc)
                    cnxexc = ConnectError(f"{pre}: {reason}")
                elif isinstance(exc, InvalidCredentials):
                    cnxexc = ConnectError(f"{pre}: Invalid Credentials supplied")
                else:
                    cnxexc = ConnectError(f"{pre}: {exc}")
                cnxexc.exc = exc
                raise cnxexc

            self.STARTED = True
            LOG.info(str(self))

    @property
    def users(self) -> Users:
        """Work with user assets."""
        self.start()
        if not hasattr(self, "_users"):
            self._users = Users(**self.API_ARGS)
        return self._users

    @property
    def devices(self) -> Devices:
        """Work with device assets."""
        self.start()
        if not hasattr(self, "_devices"):
            self._devices = Devices(**self.API_ARGS)
        return self._devices

    @property
    def adapters(self) -> Adapters:
        """Work with adapters and adapter connections."""
        self.start()
        if not hasattr(self, "_adapters"):
            self._adapters = Adapters(**self.API_ARGS)
        return self._adapters

    @property
    def instances(self) -> Instances:
        """Work with instances."""
        self.start()
        if not hasattr(self, "_instances"):
            self._instances = Instances(**self.API_ARGS)
        return self._instances

    @property
    def dashboard(self) -> Dashboard:
        """Work with dashboards and discovery cycles."""
        self.start()
        if not hasattr(self, "_dashboard"):
            self._dashboard = Dashboard(**self.API_ARGS)
        return self._dashboard

    @property
    def enforcements(self) -> Enforcements:
        """Work with Enforcement Center."""
        self.start()
        if not hasattr(self, "_enforcements"):
            self._enforcements = Enforcements(**self.API_ARGS)
        return self._enforcements

    @property
    def run_actions(self) -> RunAction:  # pragma: no cover
        """Work with Enforcement Center actions."""
        self.start()
        if not hasattr(self, "_run_actions"):
            self._run_actions = RunAction(**self.API_ARGS)
        return self._run_actions

    @property
    def system(self) -> System:  # TODO: DOCS???
        """Work with users, roles, global settings, and more."""
        self.start()
        if not hasattr(self, "_system"):
            self._system = System(**self.API_ARGS)
        return self._system

    def __init__(
        self,
        url: str,
        key: str,
        secret: str,
        log_console: bool = False,
        log_file: bool = False,
        certpath: Optional[Union[str, pathlib.Path]] = None,
        certverify: bool = False,
        certwarn: bool = True,
        proxy: Optional[str] = None,
        **kwargs,
    ):
        """Easy all-in-one connection handler.

        Args:
            url: URL, hostname, or IP address of Axonius instance
            key: API Key from account page in Axonius instance
            secret: API Secret from account page in Axonius instance
            log_console: enable logging to console
            log_file: enable logging to file
            certpath: path to CA bundle file to use when verifying certs offered by :attr:`url`
            certverify: raise exception if cert is self-signed or only if cert is invalid
            certwarn: show insecure warning once or never show insecure warning
            proxy: proxy to use when making https requests to :attr:`url`
            **kwargs: documented as properties
        """
        self.url: str = url
        """URL of Axonius instance to use"""

        self.TIMEOUT_CONNECT: int = kwargs.get("timeout_connect", TIMEOUT_CONNECT)
        """Seconds to wait for connections to open to :attr:`url` ``kwargs=timeout_connect``"""

        self.TIMEOUT_RESPONSE: int = kwargs.get("timeout_response", TIMEOUT_RESPONSE)
        """Seconds to wait for responses from :attr:`url` ``kwargs=timeout_response``"""

        self.CERT_CLIENT_KEY: Optional[Union[str, pathlib.Path]] = kwargs.get(
            "cert_client_key", None
        )
        """Private key file for cert_client_cert ``kwargs=cert_client_key``"""

        self.CERT_CLIENT_CERT: Optional[Union[str, pathlib.Path]] = kwargs.get(
            "cert_client_cert", None
        )
        """cert file to offer to :attr:`url` ``kwargs=cert_client_cert``"""

        self.CERT_CLIENT_BOTH: Optional[Union[str, pathlib.Path]] = kwargs.get(
            "cert_client_both", None
        )
        """cert file with both private key and cert to offer to :attr:`url`
        ``kwargs=cert_client_both``"""

        self.SAVE_HISTORY: bool = kwargs.get("save_history", False)
        """append responses to :attr:`axonius_api_client.http.Http.HISTORY`
        ``kwargs=save_history``"""

        self.LOG_LEVEL: Union[str, int] = kwargs.get("log_level", "debug")
        """log level for this class ``kwargs=log_level``"""

        self.LOG_REQUEST_ATTRS: Optional[List[str]] = kwargs.get("log_request_attrs", None)
        """request attrs to log :attr:`axonius_api_client.constants.REQUEST_ATTR_MAP`
        ``kwargs=log_request_attrs``"""

        self.LOG_RESPONSE_ATTRS: Optional[List[str]] = kwargs.get("log_response_attrs", None)
        """response attrs to log :attr:`axonius_api_client.constants.RESPONSE_ATTR_MAP`
        ``kwargs=log_response_attrs``"""

        self.LOG_REQUEST_BODY: bool = kwargs.get("log_request_body", False)
        """log request bodies ``kwargs=log_request_body``"""

        self.LOG_RESPONSE_BODY: bool = kwargs.get("log_response_body", False)
        """log response bodies ``kwargs=log_response_body``"""

        self.LOG_LOGGER: logging.Logger = kwargs.get("log_logger", LOG)
        """logger to use as package root logger ``kwargs=log_logger``"""

        self.LOG_LEVEL_PACKAGE: Union[str, int] = kwargs.get("log_level_package", LOG_LEVEL_PACKAGE)
        """log level for entire package ``kwargs=log_level_package``"""

        self.LOG_LEVEL_HTTP: Union[str, int] = kwargs.get("log_level_http", LOG_LEVEL_HTTP)
        """log level for :obj:`axonius_api_client.http.Http` ``kwargs=log_level_http``"""

        self.LOG_LEVEL_AUTH: Union[str, int] = kwargs.get("log_level_auth", LOG_LEVEL_AUTH)
        """log level for :obj:`axonius_api_client.auth.models.Mixins` ``kwargs=log_level_auth``"""

        self.LOG_LEVEL_API: Union[str, int] = kwargs.get("log_level_api", LOG_LEVEL_API)
        """log level for :obj:`axonius_api_client.api.mixins.ModelMixins`
        ``kwargs=log_level_api``"""

        self.LOG_LEVEL_CONSOLE: Union[str, int] = kwargs.get("log_level_console", LOG_LEVEL_CONSOLE)
        """log level for logs sent to console ``kwargs=log_level_console``"""

        self.LOG_LEVEL_FILE: Union[str, int] = kwargs.get("log_level_file", LOG_LEVEL_FILE)
        """log level for logs sent to file ``kwargs=log_level_file``"""

        self.LOG_CONSOLE_FMT: str = kwargs.get("log_console_fmt", LOG_FMT_BRIEF)
        """logging format to use for logs sent to console ``kwargs=log_console_fmt``"""

        self.LOG_FILE_FMT: str = kwargs.get("log_file_fmt", LOG_FMT_VERBOSE)
        """logging format to use for logs sent to file ``kwargs=log_file_fmt``"""

        self.LOG_FILE_NAME: Union[str, pathlib.Path] = kwargs.get("log_file_name", LOG_FILE_NAME)
        """name of file to write logs to under :attr:`LOG_FILE_PATH` ``kwargs=log_file_name``"""

        self.LOG_FILE_PATH: Union[str, pathlib.Path] = kwargs.get("log_file_path", LOG_FILE_PATH)
        """path to write :attr:`LOG_FILE_NAME` to ``kwargs=log_file_path``"""

        self.LOG_FILE_MAX_MB: int = kwargs.get("log_file_max_mb", LOG_FILE_MAX_MB)
        """rollover file logs at this many MB ``kwargs=log_file_max_mb``"""

        self.LOG_FILE_MAX_FILES: int = kwargs.get("log_file_max_files", LOG_FILE_MAX_FILES)
        """number of rollover file logs to keep ``kwargs=log_file_max_files``"""

        self.WRAPERROR: bool = kwargs.get("wraperror", True)
        """wrap errors in human friendly way or show full traceback ``kwargs=wraperror``"""

        self.LOG: logging.Logger = get_obj_log(obj=self, level=self.LOG_LEVEL)
        """logger object to use"""

        set_log_level(obj=self.LOG_LOGGER, level=self.LOG_LEVEL_PACKAGE)

        self.STARTED: bool = False
        """track if :meth:`start` has been called"""

        self.HANDLER_FILE: logging.handlers.RotatingFileHandler = None
        """file logging handler"""

        self.HANDLER_CON: logging.StreamHandler = None
        """console logging handler"""

        if log_console:
            self.HANDLER_CON = add_stderr(
                obj=self.LOG_LOGGER, level=self.LOG_LEVEL_CONSOLE, fmt=self.LOG_CONSOLE_FMT
            )

        if log_file:
            self.HANDLER_FILE = add_file(
                obj=self.LOG_LOGGER,
                level=self.LOG_LEVEL_FILE,
                file_path=self.LOG_FILE_PATH,
                file_name=self.LOG_FILE_NAME,
                max_mb=self.LOG_FILE_MAX_MB,
                max_files=self.LOG_FILE_MAX_FILES,
                fmt=self.LOG_FILE_FMT,
            )

        self.HTTP_ARGS: dict = {
            "url": url,
            "https_proxy": proxy,
            "certpath": certpath,
            "certwarn": certwarn,
            "certverify": certverify,
            "cert_client_both": self.CERT_CLIENT_BOTH,
            "cert_client_cert": self.CERT_CLIENT_CERT,
            "cert_client_key": self.CERT_CLIENT_KEY,
            "log_level": self.LOG_LEVEL_HTTP,
            "log_request_attrs": self.LOG_REQUEST_ATTRS,
            "log_response_attrs": self.LOG_RESPONSE_ATTRS,
            "log_request_body": self.LOG_REQUEST_BODY,
            "log_response_body": self.LOG_RESPONSE_BODY,
            "save_history": self.SAVE_HISTORY,
            "connect_timeout": self.TIMEOUT_CONNECT,
            "response_timeout": self.TIMEOUT_RESPONSE,
        }
        """arguments to use for creating :attr:`HTTP`"""

        self.AUTH_ARGS: dict = {"key": key, "secret": secret, "log_level": self.LOG_LEVEL_AUTH}
        """arguments to use for creating :attr:`AUTH`"""

        self.HTTP = Http(**self.HTTP_ARGS)
        """:obj:`axonius_api_client.http.Http` client to use for :attr:`AUTH`"""

        self.AUTH = ApiKey(http=self.HTTP, **self.AUTH_ARGS)
        """:obj:`axonius_api_client.auth.api_key.ApiKey` auth method to use for all API models"""

        self.API_ARGS: dict = {"auth": self.AUTH, "log_level": self.LOG_LEVEL_API}
        """arguments to use for all API models"""

    def __str__(self) -> str:
        """Show object info."""
        client = getattr(self, "HTTP", "")
        url = getattr(client, "URL", self.HTTP_ARGS["url"])
        if self.STARTED:
            about = self.system.meta.about()
            version = about.get("Version", "") or "DEMO"
            version = version.replace("_", ".")
            built = about.get("Build Date", "")
            return (
                f"Connected to {url!r} version {version} (RELEASE DATE: {built})"
                f" with API Client v{VERSION}"
            )
        else:
            return f"Not connected to {url!r}"

    def __repr__(self) -> str:
        """Show object info."""
        return self.__str__()

    @classmethod
    def _get_exc_reason(cls, exc: Exception) -> str:
        """Trim exceptions down to a more user friendly display.

        Uses :attr:`REASON_RES` to do regex substituions.
        """
        reason = str(exc)
        for reason_re in cls.REASON_RES:
            if reason_re.search(reason):
                return reason_re.sub(r"\1", reason).rstrip("')")
        return reason
