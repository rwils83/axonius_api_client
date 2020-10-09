# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import click
from ..context import CONTEXT_SETTINGS
from ..options import add_options
from ..options import AUTH
from ..options import EXPORT
from ..options import FIELDS_SELECT
from ..options import get_option_fields_default
from ..options import get_option_help
from ..options import PAGING
from ..options import QUERY
from .grp_common import GET_EXPORT
from .grp_common import load_whitelist
from .grp_common import load_wiz
from .grp_common import WIZ

OPTIONS = [
    *AUTH,
    *PAGING,
    *EXPORT,
    *GET_EXPORT,
    *FIELDS_SELECT,
    get_option_fields_default(default=True),
    *QUERY,
    *WIZ,
    get_option_help(
        choices=["auth", "query", "assetexport", "selectfields", "wizard"]),
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx,
        url,
        key,
        secret,
        query_file,
        wizard_content,
        whitelist=None,
        **kwargs):
    """Get assets using a query and fields."""
    if query_file:
        kwargs["query"] = query_file.read().strip()

    kwargs["report_software_whitelist"] = load_whitelist(whitelist)

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        kwargs = load_wiz(apiobj=apiobj,
                          wizard_content=wizard_content,
                          kwargs=kwargs)
        apiobj.get(**kwargs)
