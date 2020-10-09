# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import click
from ...context import CONTEXT_SETTINGS
from ...options import add_options
from ...options import AUTH
from ...options import INPUT_FILE
from .grp_common import EXPORT
from .grp_common import SECTION
from .grp_common import str_section

OPTIONS = [*AUTH, EXPORT, SECTION, INPUT_FILE]


@click.command(name="update-section-from-json",
               context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
        ctx,
        url,
        key,
        secret,
        input_file,
        section,
        export_format,
        **kwargs,
):
    """Update a section from a JSON file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    new_config = ctx.obj.read_stream_json(stream=input_file, expect=dict)

    apiname = ctx.parent.command.name.replace("-", "_")
    apiobj = getattr(client.system, apiname)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        settings = apiobj.update_section(section=section, **new_config)
        ctx.obj.echo_ok(f"Updated {section!r} with configuration {new_config}")
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
