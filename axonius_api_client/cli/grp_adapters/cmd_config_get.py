# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import click
from ..context import CONTEXT_SETTINGS
from ..options import add_options
from ..options import AUTH
from ..options import NODE
from .grp_common import CONFIG_EXPORT
from .grp_common import config_export
from .grp_common import CONFIG_TYPE

OPTIONS = [
    *AUTH,
    CONFIG_EXPORT,
    CONFIG_TYPE,
    *NODE,
]


@click.command(name="config-get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get adapter advanced settings."""
    """Pass."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.config_get(**kwargs)

    config_export(ctx=ctx, rows=rows, export_format=export_format)
