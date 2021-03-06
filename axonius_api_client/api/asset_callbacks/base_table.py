# -*- coding: utf-8 -*-
"""Table export callbacks class."""
from typing import List, Optional, Tuple, Union

import tabulate

from ...constants import TABLE_FORMAT, TABLE_MAX_ROWS
from ...exceptions import ApiError
from ...tools import listify
from .base import Base


class Table(Base):
    """Table export callbacks class.

    Notes:
        See :meth:`args_map` for the arguments this callbacks class.
    """

    CB_NAME: str = "table"
    """name for this callback"""

    def _init(self):
        """Override defaults in GETARGS to make table export readable."""
        self.GETARGS["field_null"] = True
        self.GETARGS["field_flatten"] = True
        self.GETARGS["field_join"] = True

        if self.GETARGS.get("field_titles", None) is None:
            self.GETARGS["field_titles"] = True

        table_api_fields = self.GETARGS.get("table_api_fields", False)
        if not table_api_fields:
            field_excludes = listify(self.GETARGS.get("field_excludes", []))
            self.GETARGS["field_excludes"] = field_excludes + self.APIOBJ.FIELDS_API

        table_max_rows = self.GETARGS.get("table_max_rows", TABLE_MAX_ROWS)
        self.GETARGS["table_max_rows"] = table_max_rows

        table_format = self.GETARGS.get("table_format", TABLE_FORMAT) or TABLE_FORMAT
        self.check_table_format(fmt=table_format)
        self.GETARGS["table_format"] = table_format

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Table, self).start(**kwargs)
        self._rows = []
        self.open_fd()

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        super(Table, self).stop(**kwargs)
        tablefmt = self.GETARGS["table_format"]
        rows = getattr(self, "_rows", [])

        table = tabulate.tabulate(
            tabular_data=rows,
            tablefmt=tablefmt,
            showindex=False,
            headers="keys",
        )

        self._fd.write(table)
        self._fd.write("\n")
        self.close_fd()

    def process_row(self, row: Union[List[dict], dict]) -> List[dict]:
        """Process the callbacks for current row.

        Args:
            row: row to process
        """
        rows = listify(row)
        rows = self.do_pre_row(rows=rows)
        self.check_stop()
        rows = self.do_row(rows=rows)
        # TBD textwrap key/values
        self._rows += rows
        return rows

    def check_stop(self):
        """Check if rows processed is greater than table_max_rows."""
        max_rows = self.GETARGS["table_max_rows"]
        rows_processed = self.STATE.get("rows_processed_total", 0)

        if all([rows_processed, max_rows]) and rows_processed >= max_rows:
            self.STATE["stop_fetch"] = True
            self.STATE["stop_msg"] = f"table_max_rows of {max_rows}"

    def check_table_format(self, fmt: str):
        """Check if table_format is valid choice.

        Args:
            fmt: table format to check

        Raises:
            :exc:`axonius_api_client.exceptions.ApiError`: if fmt is not a valid choice
        """
        if fmt not in tabulate.tabulate_formats:
            fmts = ", ".join(tabulate.tabulate_formats)
            msg = f"{fmt!r} is not a valid table format, must be one of {fmts}"
            self.echo(msg=msg, error=ApiError)

    @classmethod
    def args_map(cls) -> List[Tuple[str, str, Optional[Union[list, bool, str, int]]]]:
        """Argument maps specific to this callbacks class."""
        args = super(Table, cls).args_map()
        return args + [
            ("table_format", "Use table format:", TABLE_FORMAT),
            ("table_max_rows", "Maximum table rows:", TABLE_MAX_ROWS),
            ("table_api_fields", "Include API fields:", False),
        ]
