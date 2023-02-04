#!/usr/bin/env python3
# coding: utf-8
"""Define the init file, to be called by the main."""

from .zoomdl import ZoomDL
from .utils import parseOpts
import sys


def main():
    """Get parsed options, sanity check them, then call ZoomDL."""
    args = parseOpts(sys.argv[1:])

    if args.log_level > 5:
        raise ValueError("Log-level value should be between 0 and 5, included")

    all_urls = [args.url]  # prepare for batch reading
    zdl = ZoomDL(args)
    zdl.download(all_urls)

    sys.exit(zdl.exit_code)
