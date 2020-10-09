# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import json_dump
from ..context import click
from ..context import CONTEXT_SETTINGS
from ..options import add_options
from ..options import AUTH
from ..options import NODE
from ..options import SPLIT_CONFIG_REQ
from .grp_common import CONFIG_EXPORT
from .grp_common import config_export
from .grp_common import CONFIG_TYPE

OPTIONS = [*AUTH, CONFIG_EXPORT, CONFIG_TYPE, *NODE, SPLIT_CONFIG_REQ]


@click.command(name="config-update", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, config, **kwargs):
    """Set adapter advanced settings."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    config = dict(config)
    kwargs["kwargs_config"] = config

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.config_update(**kwargs)
    ctx.obj.echo_ok(f"Updated adapter with config:\n{json_dump(config)}")
    config_export(ctx=ctx, rows=rows, export_format=export_format)
