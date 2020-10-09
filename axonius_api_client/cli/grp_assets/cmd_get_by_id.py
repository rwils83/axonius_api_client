# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import json_dump
from ..context import click
from ..context import CONTEXT_SETTINGS
from ..options import add_options
from ..options import AUTH

OPTIONS = [
    *AUTH,
    click.option(
        "--id",
        "-i",
        "id",
        help="Internal Axon ID of asset",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="get-by-id", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get ALL data for a single asset."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = apiobj.get_by_id(**kwargs)

    click.secho(json_dump(rows))
    ctx.exit(0)
