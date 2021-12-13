#!/usr/bin/env python3
# coding: utf-8
"""Define useful methods to be used globally."""

import argparse
import os
from http.cookiejar import MozillaCookieJar
import collections
import io
import sys
from typing import List


class ZoomdlCookieJar(MozillaCookieJar):
    """Define a cookie jar.

    Code freely adapted from Youtube-DL's YoutubeCookieJar
    https://github.com/ytdl-org/youtube-dl/
    For file format, see https://curl.haxx.se/docs/http-cookies.html
    """

    _HTTPONLY_PREFIX = '#HttpOnly_'
    _ENTRY_LEN = 7
    _CookieFileEntry = collections.namedtuple(
        'CookieFileEntry',
        ('domain_name', 'include_subdomains', 'path',
         'https_only', 'expires_at', 'name', 'value'))

    def load(self, filename=None, ignore_discard=True, ignore_expires=True):
        """Load cookies from a file."""
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                raise ValueError()

        def prepare_line(line):
            # print("Prepping line '{}'".format(line))
            if line.startswith(self._HTTPONLY_PREFIX):
                line = line[len(self._HTTPONLY_PREFIX):]
            # comments and empty lines are fine
            if line.startswith('#') or not line.strip():
                return line
            cookie_list = line.split('\t')
            if len(cookie_list) != self._ENTRY_LEN:
                raise ValueError('invalid length %d' % len(cookie_list))
            cookie = self._CookieFileEntry(*cookie_list)
            if cookie.expires_at and not cookie.expires_at.isdigit():
                raise ValueError('invalid expires at %s' % cookie.expires_at)
            return line

        cf = io.StringIO()
        with io.open(filename, encoding='utf-8') as f:
            for line in f:
                try:
                    cf.write(prepare_line(line))
                except ValueError as e:
                    print(
                        'WARNING: skipping cookie file entry due to %s: %r\n'
                        % (e, line), sys.stderr)
                    continue
        cf.seek(0)
        self._really_load(cf, filename, ignore_discard, ignore_expires)
        # Session cookies are denoted by either `expires` field set to
        # an empty string or 0. MozillaCookieJar only recognizes the former
        # (see [1]). So we need force the latter to be recognized as session
        # cookies on our own.
        # Session cookies may be important for cookies-based authentication,
        # e.g. usually, when user does not check 'Remember me' check box while
        # logging in on a site, some important cookies are stored as session
        # cookies so that not recognizing them will result in failed login.
        # 1. https://bugs.python.org/issue17164
        for cookie in self:
            # Treat `expires=0` cookies as session cookies
            if cookie.expires == 0:
                cookie.expires = None
                cookie.discard = True


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


def parseOpts(args: List[str]):
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
    PARSER.add_argument("-v", "--log-level",
                        help=("Chose the level of verbosity. 0=debug, 1=info "
                              "(default), 2=warning 3=Error, 4=Critical, "
                              "5=Quiet (nothing printed)"),
                        metavar="level",
                        type=int,
                        default=1)

    PARSER.add_argument("--cookies", help=("Path to a cookies file "
                                           "in Netscape Format"),
                        metavar=("path/to/the/cookies.txt"),
                        required=False)

    PARSER.add_argument("--save-chat",
                        help=("Save chat in the meeting as a plain-text "
                              "file or .srt subtitle. "
                              "Specify mode as \"txt\" for plain-text, "
                              "or \"srt\" for .srt subtitle"),
                        metavar="mode",
                        choices=["txt", "srt"],
                        default=None)
    PARSER.add_argument("--chat-subtitle-dur",
                        help=("Duration in seconds that a chat message"
                              "appears on the screen"),
                        metavar="number",
                        type=_check_positive,
                        default=3)
    PARSER.add_argument("--save-transcript",
                        help=("Save transcripts in the meeting as a "
                              "plain-text file or .srt subtitle. Specify"
                              " mode as \"txt\" for plain-text, "
                              "or \"srt\" for .srt subtitle"),
                        metavar="mode",
                        choices=["txt", "srt"],
                        default=None)

    PARSER.add_argument("--dump-pagemeta",
                        help=("Dump page metas in json format"
                              " for further usages"),
                        default=False,
                        action='store_true')

    return PARSER.parse_args(args)
