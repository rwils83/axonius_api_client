# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from . import grp_central_core
from . import grp_discover
from . import grp_meta
from . import grp_nodes
from . import grp_roles
from . import grp_settings
from . import grp_users
from ..context import AliasedGroup


@click.group(cls=AliasedGroup)
def system():
    """Group: System control commands."""


system.add_command(grp_meta.meta)
system.add_command(grp_nodes.instances)
system.add_command(grp_central_core.central_core)
system.add_command(grp_roles.roles)
system.add_command(grp_settings.settings_lifecycle)
system.add_command(grp_settings.settings_gui)
system.add_command(grp_settings.settings_core)
system.add_command(grp_users.users)
system.add_command(grp_discover.discover)
