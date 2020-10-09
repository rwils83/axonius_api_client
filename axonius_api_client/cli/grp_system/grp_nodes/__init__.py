# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_get
from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def instances():
    """Group: Manage Instances."""


instances.add_command(cmd_get.cmd)
