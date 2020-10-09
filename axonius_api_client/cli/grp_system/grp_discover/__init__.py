# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_get
from . import cmd_start
from . import cmd_stop
from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def discover():
    """Group: Discover and Lifecycle management."""


discover.add_command(cmd_get.cmd)
discover.add_command(cmd_start.cmd)
discover.add_command(cmd_stop.cmd)
