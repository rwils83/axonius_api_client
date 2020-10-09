# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import click
from ...context import CONTEXT_SETTINGS
from ...options import add_options
from ...options import AUTH
from ...options import NODE_CNX
from .grp_common import ID_CNX
from .grp_common import PROMPTS

OPTIONS = [*AUTH, *NODE_CNX, *PROMPTS, ID_CNX]


@click.command(name="test-by-id", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, adapter_name, adapter_node, cnx_id, **kwargs):
    """Test reachability for an existing connection by ID."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        client.adapters.cnx.test_by_id(
            adapter_name=adapter_name,
            adapter_node=adapter_node,
            cnx_id=cnx_id,
        )
        ctx.obj.echo_ok(msg="Reachability test succeeded!")
