# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_about
from . import cmd_sizes
from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def meta():
    """Group: System metadata."""


meta.add_command(cmd_about.cmd)
meta.add_command(cmd_sizes.cmd)
