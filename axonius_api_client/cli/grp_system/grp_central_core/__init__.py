# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_get
from . import cmd_restore_from_aws_s3
from . import cmd_update
from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def central_core():
    """Group: Manage Central Core feature."""


central_core.add_command(cmd_get.cmd)
central_core.add_command(cmd_update.cmd)
central_core.add_command(cmd_restore_from_aws_s3.cmd)
