# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import click
from ..context import CONTEXT_SETTINGS
from ..options import add_options
from ..options import AUTH
from ..options import get_option_help
from ..options import QUERY
from .grp_common import HISTORY_DATE
from .grp_common import load_wiz
from .grp_common import WIZ

OPTIONS = [
    *AUTH,
    *QUERY,
    *WIZ,
    HISTORY_DATE,
    get_option_help(choices=["auth", "query"]),
]


@click.command(name="count", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx,
        url,
        key,
        secret,
        query_file,
        wizard_content,
        help_detailed=None,
        **kwargs):
    """Get the count of assets from a query."""
    if query_file:
        kwargs["query"] = query_file.read().strip()

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        kwargs = load_wiz(apiobj=apiobj,
                          wizard_content=wizard_content,
                          kwargs=kwargs)
        raw_data = apiobj.count(**kwargs)

    click.secho(format(raw_data))
