# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import click
from ...context import CONTEXT_SETTINGS
from ...options import add_options
from ...options import AUTH
from ...options import NODE_CNX
from ...options import SPLIT_CONFIG_OPT
from .grp_common import add_cnx
from .grp_common import EXPORT
from .grp_common import prompt_config
from .grp_common import PROMPTS

OPTIONS = [
    *AUTH,
    EXPORT,
    *NODE_CNX,
    *PROMPTS,
    SPLIT_CONFIG_OPT,
]


@click.command(name="add", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, config, **kwargs):
    """Add a connection from prompts or arguments."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    new_config = dict(config)
    prompt_config(ctx=ctx, client=client, new_config=new_config, **kwargs)
    add_cnx(ctx=ctx, client=client, new_config=new_config, **kwargs)
