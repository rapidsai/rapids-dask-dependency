"""
:ref:`UCX`_ based communications for distributed.

See :ref:`communications` for more.

.. _UCX: https://github.com/openucx/ucx
"""

from __future__ import annotations

import functools
import logging
import os
import struct
import textwrap
import warnings
import weakref
from collections.abc import Awaitable, Callable, Collection
from enum import Enum
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import dask
from dask.utils import parse_bytes

from distributed.comm.addressing import parse_host_port, unparse_host_port
from distributed.comm.core import BaseListener, Comm, CommClosedError, Connector
from distributed.comm.registry import Backend, backends
from distributed.comm.utils import ensure_concrete_host, from_frames, to_frames
from distributed.diagnostics.nvml import (
    CudaDeviceInfo,
    get_device_index_and_uuid,
    has_cuda_context,
)
from distributed.protocol.utils import host_array
from distributed.utils import ensure_ip, get_ip, get_ipv6, log_errors, nbytes


def _raise_deprecated():
    message = textwrap.dedent(
        """\
        The 'ucx' protocol was removed from Distributed because UCX-Py has been deprecated.
        To continue using protocol='ucx', please install 'distributed-ucxx' (conda-forge)
        or 'distributed-ucxx-cu[12,13]' (PyPI, selecting 12 for CUDA version 12.*, and 13
        for CUDA version 13.*).
        """
    )
    warnings.warn(message, FutureWarning)
    raise FutureWarning(message)


class UCXDeprecated(Comm):
    def __init__(self):
        _raise_deprecated()


class UCXConnectorDeprecated(Connector):
    prefix = "ucx://"
    comm_class = UCXDeprecated
    encrypted = False


class UCXListenerDeprecated(BaseListener):
    prefix = UCXConnectorDeprecated.prefix
    comm_class = UCXConnectorDeprecated.comm_class
    encrypted = UCXConnectorDeprecated.encrypted

    def __init__(
        self,
        address: str,
        comm_handler: Callable[[UCXDeprecated], Awaitable[None]] | None = None,
        deserialize: bool = False,
        allow_offload: bool = True,
        **connection_args: Any,
    ):
        _raise_deprecated()

    @property
    def port(self):
        return self.ucp_server.port

    async def start(self):
        _raise_deprecated()

    def stop(self):
        _raise_deprecated()

    @property
    def listen_address(self):
        _raise_deprecated()

    @property
    def contact_address(self):
        _raise_deprecated()


class UCXBackendDeprecated(Backend):
    def get_connector(self):
        return UCXConnectorDeprecated()

    def get_listener(self, loc, handle_comm, deserialize, **connection_args):
        return UCXListenerDeprecated(loc, handle_comm, deserialize, **connection_args)

    def get_address_host(self, loc):
        _raise_deprecated()

    def resolve_address(self, loc):
        _raise_deprecated()

    def get_local_address_for(self, loc):
        _raise_deprecated()


class UCXConnectorOldDeprecated(UCXConnectorDeprecated):
    prefix = "ucx-old://"


class UCXListenerOldDeprecated(UCXListenerDeprecated):
    prefix = UCXConnectorOldDeprecated.prefix


class UCXBackendOldDeprecated(UCXBackendDeprecated):
    def get_connector(self):
        return UCXConnectorOldDeprecated()

    def get_listener(self, loc, handle_comm, deserialize, **connection_args):
        return UCXListenerOldDeprecated(loc, handle_comm, deserialize, **connection_args)


def _rewrite_ucxx_backend():
    try:
        from distributed_ucxx.ucxx import UCXX, UCXXBackend, UCXXConnector, UCXXListener

        class UCXXPrefixRewrite(UCXX):
            prefix = "ucx://"

        class UCXXConnectorPrefixRewrite(UCXXConnector):
            prefix = "ucx://"
            comm_class = UCXXPrefixRewrite

        class UCXXListenerPrefixRewrite(UCXXListener):
            prefix = UCXXConnectorPrefixRewrite.prefix
            comm_class = UCXXConnectorPrefixRewrite.comm_class
            encrypted = UCXXConnectorPrefixRewrite.encrypted

        class UCXXBackendPrefixRewrite(UCXXBackend):
            def get_connector(self):
                return UCXXConnectorPrefixRewrite()

            def get_listener(self, loc, handle_comm, deserialize, **connection_args):
                return UCXXListenerPrefixRewrite(loc, handle_comm, deserialize, **connection_args)


        return UCXXBackendPrefixRewrite
    except ImportError:
        return UCXBackendDeprecated


backends["ucx"] = _rewrite_ucxx_backend()()
backends["ucx-old"] = UCXBackendOldDeprecated()
