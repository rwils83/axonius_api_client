# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_config_get
from . import cmd_config_update
from . import cmd_config_update_from_json
from . import cmd_file_upload
from . import cmd_get
from . import grp_cnx
from ..context import AliasedGroup


@click.group(cls=AliasedGroup)
def adapters():
    """Group: Work with adapters and adapter connections."""


adapters.add_command(cmd_get.cmd)
adapters.add_command(cmd_config_get.cmd)
adapters.add_command(cmd_config_update.cmd)
adapters.add_command(cmd_config_update_from_json.cmd)
adapters.add_command(cmd_file_upload.cmd)
adapters.add_command(grp_cnx.cnx)
