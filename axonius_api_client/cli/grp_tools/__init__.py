# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_convert_cert
from . import cmd_shell
from . import cmd_signup
from . import cmd_sysinfo
from . import cmd_write_config
from ..context import AliasedGroup


@click.group(cls=AliasedGroup)
def tools():
    """Group: CLI tools."""


tools.add_command(cmd_shell.cmd)
tools.add_command(cmd_write_config.cmd)
tools.add_command(cmd_sysinfo.cmd)
tools.add_command(cmd_signup.cmd)
tools.add_command(cmd_convert_cert.cmd)
