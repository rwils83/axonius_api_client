# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
# from ....exceptions import CnxAddError
from ...context import click
from ...context import CONTEXT_SETTINGS
from ...options import add_options
from ...options import AUTH
from ...options import INPUT_FILE
from ...options import NODE_CNX
from .grp_common import add_cnx
from .grp_common import EXPORT

OPTIONS = [
    *AUTH,
    EXPORT,
    *NODE_CNX,
    INPUT_FILE,
]


@click.command(name="add-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, **kwargs):
    """Add a connection from a JSON file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    new_config = ctx.obj.read_stream_json(stream=input_file, expect=dict)
    add_cnx(ctx=ctx, client=client, new_config=new_config, **kwargs)
