#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2010 Nathaniel Smith <njs@pobox.com>
# Copyright (C) 2011-2018 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import os

from xpra.util import envbool

#defaults which may be overridden by platform_import:
CAN_DAEMONIZE = True
REINIT_WINDOWS = False
AUTOSTART = False

INPUT_DEVICES = ["auto"]

SOURCE = []

SYSTEM_PROXY_SOCKET = os.environ.get("XPRA_SYSTEM_PROXY_SOCKET", "/run/xpra/system")

CLIPBOARDS = []
CLIPBOARD_WANT_TARGETS = envbool("XPRA_CLIPBOARD_WANT_TARGETS")
CLIPBOARD_GREEDY = envbool("XPRA_CLIPBOARD_GREEDY")
CLIPBOARD_PREFERRED_TARGETS = ("UTF8_STRING", "TEXT", "STRING", "text/plain")

EXECUTABLE_EXTENSION = ""

OPEN_COMMAND = []

COMMAND_SIGNALS = ()

DEFAULT_START_ENV = []
DEFAULT_ENV = []

#DEFAULT_SSH_COMMAND = "paramiko"
DEFAULT_SSH_COMMAND = "ssh -x"
DEFAULT_PULSEAUDIO_CONFIGURE_COMMANDS = [
                                         ["pactl", "set-default-sink", "Xpra-Speaker"],
                                         ["pactl", "set-default-source", "Xpra-Microphone.monitor"],
                                         ]


SOCKET_OPTIONS = (
    "SO_BROADCAST", "SO_RCVLOWAT",
    "SO_DONTROUTE", "SO_ERROR", "SO_EXCLUSIVEADDRUSE",
    "SO_KEEPALIVE", "SO_LINGER", "SO_OOBINLINE", "SO_RCVBUF",
    "SO_RCVTIMEO", "SO_REUSEADDR", "SO_REUSEPORT",
    "SO_SNDBUF", "SO_SNDTIMEO", "SO_TIMEOUT", "SO_TYPE",
    )
IP_OPTIONS = (
    #"IP_MULTICAST_IF", "IP_MULTICAST_LOOP", "IP_MULTICAST_TTL",
    "IP_DONTFRAG", "IP_OPTIONS", "IP_RECVLCLIFADDR",
    "IP_RECVPKTINFO", "IP_TOS", "IP_TTL",
    )
TCP_OPTIONS = ("TCP_NODELAY", "TCP_MAXSEG", "TCP_KEEPALIVE")


_features_list_ = [
                   "AUTOSTART",
                   "CAN_DAEMONIZE",
                   "REINIT_WINDOWS",
                   "COMMAND_SIGNALS",
                   "SOURCE",
                   "DEFAULT_ENV",
                   "DEFAULT_START_ENV",
                   "DEFAULT_SSH_COMMAND",
                   "DEFAULT_PULSEAUDIO_CONFIGURE_COMMANDS",
                   "CLIPBOARDS",
                   "CLIPBOARD_WANT_TARGETS",
                   "CLIPBOARD_GREEDY",
                   "CLIPBOARD_PREFERRED_TARGETS",
                   "EXECUTABLE_EXTENSION",
                   "INPUT_DEVICES",
                   "SYSTEM_PROXY_SOCKET",
                   "OPEN_COMMAND",
                   "SOCKET_OPTIONS",
                   "IP_OPTIONS",
                   "TCP_OPTIONS",
                   ]
from xpra.platform import platform_import
platform_import(globals(), "features", False,
                *_features_list_)


def main():
    from xpra.util import print_nested_dict
    from xpra.platform import program_context
    with program_context("Features-Info", "Features Info"):
        d = {}
        for k in _features_list_:
            d[k] = globals()[k]
        print_nested_dict(d)


if __name__ == "__main__": # pragma: no cover
    main()
