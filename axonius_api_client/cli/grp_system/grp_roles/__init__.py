# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_add
from . import cmd_delete
from . import cmd_get
from . import cmd_get_by_name
from . import cmd_update
from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def roles():
    """Group: Manage Roles."""


roles.add_command(cmd_get.cmd)
roles.add_command(cmd_get_by_name.cmd)
roles.add_command(cmd_delete.cmd)
roles.add_command(cmd_add.cmd)
roles.add_command(cmd_update.cmd)
