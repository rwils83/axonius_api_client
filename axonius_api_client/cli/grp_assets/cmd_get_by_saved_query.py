# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import click
from ..context import CONTEXT_SETTINGS
from ..options import add_options
from ..options import AUTH
from ..options import EXPORT
from ..options import FIELDS_SELECT
from ..options import get_option_help
from ..options import PAGING
from ..options import SQ_NAME
from .grp_common import GET_EXPORT
from .grp_common import load_whitelist

METHOD = "get-by-saved-query"
OPTIONS = [
    *AUTH,
    *PAGING,
    *EXPORT,
    *GET_EXPORT,
    *FIELDS_SELECT,
    SQ_NAME,
    get_option_help(choices=["auth", "assetexport", "selectfields"]),
]


@click.command(name="get-by-saved-query", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, whitelist=None, **kwargs):
    """Get assets using a saved query."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    kwargs["report_software_whitelist"] = load_whitelist(whitelist)

    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        apiobj.get_by_saved_query(**kwargs)
