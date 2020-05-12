#!/usr/bin/env python3
from __future__ import unicode_literals

import sys

if __package__ is None and not hasattr(sys, 'frozen'):
    # direct call of __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(path))
    print(os.path.dirname(path))

import zoom_dl
import requests

if __name__ == '__main__':
    import argparse
    PARSER = argparse.ArgumentParser(
        description="Utility to download zoom videos",
        prog="zoomdl",
        formatter_class=lambda prog: argparse.HelpFormatter(prog,
                                                            max_help_position=10,
                                                            width=200)
    )

    PARSER.add_argument("-u", "--url",
                        help="Enter the url of the video to download. Looks like 'zoom.us/rec/play/...'",
                        type=str,
                        required=True,
                        metavar="zoom url")
    PARSER.add_argument("-f", "--filename",
                        help="The name of the output video file without extension. Default to the filename according to Zoom. Extension is automatic.",
                        metavar="filename")
    PARSER.add_argument("-p", "--password",
                        help="Password of the video (if any)",
                        metavar="password")
    args = PARSER.parse_args()
    zoom_dl.zoomdl(args.url, args.filename, args.password)
