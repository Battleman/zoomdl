#!/usr/bin/env python3
# coding: utf-8
"""Define useful methods to be used globally."""

import argparse
import os


def _check_positive(value):
    """Ensure a given value is a positive integer."""
    int_value = int(value)
    if int_value < 0:
        raise argparse.ArgumentTypeError(
            "%s is an invalid positive int value" % value)
    return int_value


def _valid_path(value):
    if not (os.path.exists(value) and os.path.isfile(value)):
        raise argparse.ArgumentTypeError(
            "%s doesn't seem to be a valid file." & value)
    return value


def parseOpts():
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Namespace of the parsed arguments.
    """
    PARSER = argparse.ArgumentParser(
        description="Utility to download zoom videos",
        prog="zoomdl",
        formatter_class=(lambda prog:
                         argparse.HelpFormatter(prog,
                                                max_help_position=10,
                                                width=200)
                         ))

    PARSER.add_argument("-u", "--url",
                        help=("Enter the url of the video to download. "
                              "Looks like 'zoom.us/rec/play/...'"),
                        type=str,
                        required=True,
                        metavar="url")
    PARSER.add_argument("-f", "--filename",
                        help=("The name of the output video file without "
                              "extension. Default to the filename according "
                              "to Zoom. Extension is automatic."),
                        metavar="filename")
    PARSER.add_argument("-d", "--filename-add-date",
                        help=("Add video meeting date if it is specified. "
                              "Default is not to include the date."),
                        default=False,
                        action='store_true')
    PARSER.add_argument("--user-agent",
                        help=("Use custom user agent."
                              "Default is real browser user agent."),
                        type=str)
    PARSER.add_argument("-p", "--password",
                        help="Password of the video (if any)",
                        metavar="password")
    PARSER.add_argument("-c", "--count-clips",
                        help=("If multiple clips, how many to download. "
                              "1 = only current URL (default). "
                              "0 = all of them. "
                              "Other positive integer, count of clips to "
                              "download, starting from the current one"),
                        metavar="Count",
                        type=_check_positive,
                        default=1)
    PARSER.add_argument("--cookies-jar",
                        help="Path to a custom cookie jar", metavar="Path", type=_valid_path)
    PARSER.add_argument("-v", "--log-level",
                        help=("Chose the level of verbosity. 0=debug, 1=info "
                              "(default), 2=warning 3=Error, 4=Critical, "
                              "5=Quiet (nothing printed)"),
                        metavar="level",
                        type=int,
                        default=1)
    # 3 commands on cookies... #FIXME
    PARSER.add_argument("-r", "--recordmeet",
                        help=("Enter the _zm_web_recordmeet cookie. "),
                        type=str,
                        required=False,
                        default="",
                        metavar="recordmeet")
    PARSER.add_argument("-k", "--kms",
                        help=("Enter the _zm_kms cookie (for SSO). "),
                        type=str,
                        required=False,
                        default="",
                        metavar="kms")
    PARSER.add_argument("-a", "--auth",
                        help=("Set SSO Authentication cookies _zm_kms and"
                              "_zm_ssid cookies cookies"
                              "Looks like: 'aw1_*******'"),
                        type=str,
                        default="",
                        metavar="auth")
    # PARSER.add_argument("-b", "--browser",
    #                     help=("Indicate the browser from which retrieve the "
    #                           "cookies, to bypass passwords and reCAPTCHA. "
    #                           "Currently supported: Firefox and Chrome."),
    #                     metavar="Browser")
    return PARSER.parse_args()
