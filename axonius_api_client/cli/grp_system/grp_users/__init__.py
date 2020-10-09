# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_add
from . import cmd_add_from_csv
from . import cmd_delete
from . import cmd_email_password_reset_link
from . import cmd_get
from . import cmd_get_by_name
from . import cmd_get_password_reset_link
from . import cmd_update
from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def users():
    """Group: Manage Users."""


users.add_command(cmd_get.cmd)
users.add_command(cmd_get_by_name.cmd)
users.add_command(cmd_update.cmd)
users.add_command(cmd_delete.cmd)
users.add_command(cmd_get_password_reset_link.cmd)
users.add_command(cmd_email_password_reset_link.cmd)
users.add_command(cmd_add.cmd)
users.add_command(cmd_add_from_csv.cmd)
