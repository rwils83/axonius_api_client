# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import click
from ...context import CONTEXT_SETTINGS
from ...options import add_options
from ...options import AUTH
from .grp_common import ALLOW
from .grp_common import DENY
from .grp_common import EXPORT
from .grp_common import handle_export
from .grp_common import ROLE_NAME

OPTIONS = [
    *AUTH,
    EXPORT,
    ROLE_NAME,
    ALLOW,
    DENY,
]


@click.command(name="update", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, name, **kwargs):
    """Update a roles permissions."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system.roles.update(name=name, **kwargs)
        ctx.obj.echo_ok(f"Updated role {name!r}")

    handle_export(ctx=ctx, data=data, export_format=export_format, **kwargs)
