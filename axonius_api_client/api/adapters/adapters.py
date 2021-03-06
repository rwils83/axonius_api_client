# -*- coding: utf-8 -*-
"""API for working with adapters."""
import pathlib
from typing import List, Optional, Union

from ...constants import CONFIG_TYPES, DEFAULT_NODE
from ...exceptions import ApiError, NotFoundError
from ...tools import path_read
from ..mixins import ModelMixins
from ..parsers import (
    config_build,
    config_unchanged,
    config_unknown,
    parse_adapters,
    parse_schema,
    tablize_adapters,
)
from ..routers import API_VERSION, Router
from .cnx import Cnx


class Adapters(ModelMixins):
    """API object for working with adapters.

    Examples:
        First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

        >>> # Get an adapter by name
        >>> adapter = client.adapters.get_by_name(name="aws")
        >>> print(adapter['status'])  # overall adapter status
        >>> print(adapter['cnx_count_total'])  # total connection count
        >>> print(adapter['cnx_count_broken'])  # broken connection count
        >>> print(adapter['cnx_count_working'])  # working connection count
        >>>
        >>> # Get details of each connection of the adapter
        >>> for cnx in adapter["cnx"]:
        ...     print(cnx)
        ...     print(cnx["working"])  # bool if connection is working or not
        ...     print(cnx["error"])  # error from last fetch attempt
        ...     print(cnx["config"])  # configuration of connection
        ...     print(cnx["id"])  # ID of connection
        ...     print(cnx["uuid"])  # UUID of connection
        >>>
        >>> # Update the generic advanced settings for the adapter
        >>> updated_config = client.adapters.config_update(
        ...     name="aws", last_seen_threshold_hours=24
        ... )
        >>>
        >>> # Update the adapter specific advanced settings
        >>> updated_config = client.adapters.config_update(
        ...     name="aws", config_type="specific", fetch_s3=True
        ... )
        >>>
        >>> # Update the discover advanced settings
        >>> # XXX currently broken!
        >>>
        >>> # Upload a file for use in a connection later
        >>> file_uuid = client.adapters.file_upload_path(path="test.csv")

    """

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.adapters

    def get(self) -> List[dict]:
        """Get all adapters on all nodes."""
        parsed = parse_adapters(raw=self._get())
        parsed = sorted(parsed, key=lambda x: [x["node_name"], x["name"]])
        return parsed

    def get_by_name(self, name: str, node: str = DEFAULT_NODE) -> dict:
        """Get an adapter by name on a single node.

        Args:
            name: name of adapter to get
            node: name of node to get adapter from
        """
        adapters = self.get()

        keys = ["node_name", "node_id"]
        nodes = [x for x in adapters if node.lower() in [str(x[k]).lower() for k in keys]]

        if not nodes:
            err = f"No node named {node!r} found"
            raise NotFoundError(tablize_adapters(adapters=adapters, err=err))

        keys = ["name", "name_raw", "name_plugin"]
        for adapter in nodes:
            if any([adapter[k].lower() == name.lower() for k in keys]):
                return adapter

        err = f"No adapter named {name!r} found on node {node!r}"
        raise NotFoundError(tablize_adapters(adapters=adapters, err=err))

    def config_get(self, name: str, node: str = DEFAULT_NODE, config_type: str = "generic") -> dict:
        """Get the advanced settings for an adapter.

        Args:
            name: name of adapter to get advanced settings of
            node: name of node to get adapter from
            config_type: One of generic, specific, or discover
        """
        adapter = self.get_by_name(name=name, node=node)
        return self.config_refetch(adapter=adapter, config_type=config_type)

    def config_refetch(self, adapter: dict, config_type: str = "generic") -> dict:
        """Re-fetch the advanced settings for an adapter.

        Args:
            adapter: adapter previously fetched from :meth:`get_by_name`
            config_type: One of generic, specific, or discover
        """
        schemas = adapter["schemas"]
        name_config = f"{config_type}_name"
        name_config = schemas.get(name_config)
        name_plugin = adapter["name_plugin"]

        if not name_config:
            name = adapter["name"]
            valid = ", ".join([x for x in CONFIG_TYPES if f"{x}_name" in schemas])
            raise ApiError(f"Adapter {name} has no config type {config_type!r}, valids: {valid}!")

        data = self._config_get(name_plugin=name_plugin, name_config=name_config)

        data["schema"] = parse_schema(raw=data["schema"])

        return data

    def config_update(
        self, name: str, node: str = DEFAULT_NODE, config_type: str = "generic", **kwargs
    ) -> dict:
        """Update the advanced settings for an adapter.

        Args:
            name: name of adapter to update advanced settings of
            node: name of node to get adapter from
            config_type: One of generic, specific, or discover
            **kwargs: configuration to update advanced settings of config_type
        """
        kwargs_config = kwargs.pop("kwargs_config", {})
        kwargs.update(kwargs_config)
        adapter = self.get_by_name(name=name, node=node)

        config_map = self.config_refetch(adapter=adapter, config_type=config_type)

        name_config = f"{config_type}_name"
        name_config = adapter["schemas"][name_config]

        old_config = config_map["config"]
        schemas = config_map["schema"]

        source = f"adapter {name!r} {config_type} advanced settings"
        config_unknown(schemas=schemas, new_config=kwargs, source=source)
        new_config = config_build(
            schemas=schemas, old_config=old_config, new_config=kwargs, source=source
        )
        config_unchanged(
            schemas=schemas, old_config=old_config, new_config=new_config, source=source
        )

        self._config_update(
            name_raw=adapter["name_raw"],
            name_config=name_config,
            new_config=new_config,
        )

        return self.config_refetch(adapter=adapter, config_type=config_type)

    def file_upload(
        self,
        name: str,
        field_name: str,
        file_name: str,
        file_content: Union[str, bytes],
        file_content_type: Optional[str] = None,
        node: str = DEFAULT_NODE,
    ) -> dict:
        """Upload a file to a specific adapter on a specific node.

        Args:
            name: name of adapter to upload file to
            node: name of node to to upload file to
            field_name: name of field (should match configuration schema key name)
            file_name: name of file to upload
            file_content: content of file to upload
            file_content_type: mime type of file to upload
        """
        adapter = self.get_by_name(name=name, node=node)

        return self._file_upload(
            name_raw=adapter["name_raw"],
            node_id=adapter["node_id"],
            file_name=file_name,
            field_name=field_name,
            file_content=file_content,
            file_content_type=file_content_type,
        )

    def file_upload_path(self, path: Union[str, pathlib.Path], **kwargs):
        """Upload the contents of a file to a specific adapter on a specific node.

        Args:
            path: path to file containing contents to upload
            **kwargs: passed to :meth:`file_upload`
        """
        path, file_content = path_read(obj=path, binary=True, is_json=False)
        kwargs.setdefault("field_name", path.name)
        kwargs.setdefault("file_name", path.name)
        kwargs["file_content"] = file_content
        return self.file_upload(**kwargs)

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        self.cnx: Cnx = Cnx(parent=self)
        """Work with adapter connections"""

        super(Adapters, self)._init(**kwargs)

    def _get(self) -> dict:
        """Direct API method to get all adapters."""
        path = self.router.root
        return self.request(method="get", path=path)

    def _config_update(self, name_raw: str, name_config: str, new_config: dict) -> str:
        """Direct API method to set advanced settings for an adapter.

        Args:
            name_raw: raw name of the adapter i.e. ``aws_adapter``
            name_config: name of advanced settings to set

                * ``AdapterBase`` for generic advanced settings
                * ``AwsSettings`` for adapter specific advanced settings (name changes per adapter)
                * ``DiscoverySchema`` for discover advanced settings
            new_config: the advanced configuration key value pairs to set
        """
        path = self.router.config_set.format(
            adapter_name_raw=name_raw, adapter_config_name=name_config
        )
        return self.request(method="post", path=path, json=new_config, error_json_invalid=False)

    def _config_get(self, name_plugin: str, name_config: str) -> dict:
        """Direct API method to set advanced settings for an adapter.

        Args:
            name_plugin: plugin name of the adapter i.e. ``aws_adapter_0``
            name_config: name of advanced settings to get

                * ``AdapterBase`` for generic advanced settings
                * ``AwsSettings`` for adapter specific advanced settings (name changes per adapter)
                * ``DiscoverySchema`` for discover advanced settings
        """
        path = self.router.config_get.format(
            adapter_name_plugin=name_plugin, adapter_config_name=name_config
        )
        return self.request(method="get", path=path)

    def _file_upload(
        self,
        name_raw: str,
        node_id: str,
        field_name: str,
        file_name: str,
        file_content: Union[bytes, str],
        file_content_type: Optional[str] = None,
        file_headers: Optional[dict] = None,
    ) -> dict:
        """Direct API method to upload a file to a specific adapter on a specifc node.

        Args:
            name_raw: raw name of the adapter i.e. ``aws_adapter``
            node_id: ID of node running adapter
            field_name: name of field (should match configuration schema key name)
            file_name: name of file to upload
            file_content: content of file to upload
            file_content_type: mime type of file to upload
            file_headers: headers to use for file
        """
        data = {"field_name": field_name}
        files = {"userfile": (file_name, file_content, file_content_type, file_headers)}
        path = self.router.file_upload.format(adapter_name_raw=name_raw, adapter_node_id=node_id)
        ret = self.request(method="post", path=path, data=data, files=files)
        ret["filename"] = file_name
        return ret
