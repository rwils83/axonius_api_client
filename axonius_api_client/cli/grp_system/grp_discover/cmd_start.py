# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import click
from ...context import CONTEXT_SETTINGS
from ...options import add_options
from ...options import AUTH
from .grp_common import EXPORT
from .grp_common import handle_export

OPTIONS = [
    *AUTH,
    EXPORT,
]


@click.command(name="start", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Start the discover cycle."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.dashboard.start()

    handle_export(ctx=ctx, data=data, **kwargs)
