# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxUpdateError
from ...context import click
from ...context import CONTEXT_SETTINGS
from ...options import add_options
from ...options import AUTH
from ...options import NODE_CNX
from ...options import SPLIT_CONFIG_OPT
from .grp_common import EXPORT
from .grp_common import handle_export
from .grp_common import ID_CNX

OPTIONS = [
    *AUTH,
    EXPORT,
    *NODE_CNX,
    SPLIT_CONFIG_OPT,
    ID_CNX,
]


@click.command(name="update-by-id", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    config,
    adapter_node,
    adapter_name,
    cnx_id,
    **kwargs,
):
    """Update a connection from arguments."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    new_config = dict(config)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        try:
            cnx_new = client.adapters.cnx.update_by_id(
                adapter_name=adapter_name,
                adapter_node=adapter_node,
                cnx_id=cnx_id,
                **new_config,
            )
            ctx.obj.echo_ok(msg="Connection updated successfully!")

        except CnxUpdateError as exc:
            ctx.obj.echo_error(msg=f"{exc}", abort=False)
            cnx_new = exc.cnx_new

    handle_export(ctx=ctx, rows=cnx_new, **kwargs)
