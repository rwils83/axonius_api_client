# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_add
from . import cmd_add_from_json
from . import cmd_delete_by_id
from . import cmd_get
from . import cmd_get_by_id
from . import cmd_test
from . import cmd_test_by_id
from ... import context


@click.group(cls=context.AliasedGroup)
def cnx():
    """Group: Work with adapter connections."""


cnx.add_command(cmd_add.cmd)
cnx.add_command(cmd_add_from_json.cmd)
cnx.add_command(cmd_get.cmd)
cnx.add_command(cmd_get_by_id.cmd)
cnx.add_command(cmd_delete_by_id.cmd)
cnx.add_command(cmd_test.cmd)
cnx.add_command(cmd_test_by_id.cmd)
