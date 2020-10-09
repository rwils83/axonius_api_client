# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import click
from ...context import CONTEXT_SETTINGS
from ...options import add_options
from ...options import AUTH
from .grp_common import EXPORT
from .grp_common import handle_export
from .grp_common import ROLE_NAME

OPTIONS = [
    *AUTH,
    EXPORT,
    ROLE_NAME,
]


@click.command(name="get-by-name", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, name, **kwargs):
    """Get all roles."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system.roles.get_by_name(name=name)

    handle_export(ctx=ctx, data=data, **kwargs)
