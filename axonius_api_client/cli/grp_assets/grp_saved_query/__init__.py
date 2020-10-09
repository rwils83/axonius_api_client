# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import cmd_add
from . import cmd_add_from_json
from . import cmd_add_from_wiz_csv
from . import cmd_delete_by_name
from . import cmd_delete_by_tags
from . import cmd_get
from . import cmd_get_by_name
from . import cmd_get_by_tags
from . import cmd_get_tags
from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def saved_query():
    """Group: Work with saved queries."""


saved_query.add_command(cmd_add.cmd)
saved_query.add_command(cmd_add_from_json.cmd)
saved_query.add_command(cmd_add_from_wiz_csv.cmd)
saved_query.add_command(cmd_delete_by_name.cmd)
saved_query.add_command(cmd_delete_by_tags.cmd)
saved_query.add_command(cmd_get.cmd)
saved_query.add_command(cmd_get_tags.cmd)
saved_query.add_command(cmd_get_by_name.cmd)
saved_query.add_command(cmd_get_by_tags.cmd)
