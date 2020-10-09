# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import click
from ...context import CONTEXT_SETTINGS
from ...options import add_options
from ...options import AUTH
from .grp_common import EXPORT
from .grp_common import SECTION
from .grp_common import str_section

OPTIONS = [*AUTH, EXPORT, SECTION]


@click.command(name="get-section", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, section, export_format, **kwargs):
    """Get settings for a section."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    apiname = ctx.parent.command.name.replace("-", "_")
    apiobj = getattr(client.system, apiname)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        settings = apiobj.get_section(section=section)

    if export_format == "str":
        str_section(meta=settings)
        ctx.exit(0)

    if export_format == "json-config":
        config = settings["config"]
        click.secho(json_dump(config))
        ctx.exit(0)

    if export_format == "json-full":
        click.secho(json_dump(settings))
        ctx.exit(0)

    ctx.exit(1)
