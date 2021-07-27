#!/usr/bin/env python3
# coding: utf-8
"""Define the main ZoomDL class and its methods."""
import os
import re
import sys
from typing import Optional
import demjson
import requests
from tqdm import tqdm

from .utils import ZoomdlCookieJar


class ZoomDL():
    """Class for ZoomDL."""

    def __init__(self, args):
        """Init the class."""
        self.args = args
        self.loglevel = args.log_level
        self.page = None
        self.url, self.domain, self.subdomain = "", "", ""
        self.metadata = None
        self.session = requests.session()

        self.loglevel = self.args.log_level

        if self.args.cookies:
            cookiejar = ZoomdlCookieJar(self.args.cookies)
            cookiejar.load()
            self.session.cookies.update(cookiejar)

    def _print(self, message, level=0):
        """Print to console, if level is sufficient.

        This is meant to override the default print. When you need to
        print something, you use this and specify a level. If the level is
        sufficient, it will be printed, otherwise it will be discarded.

        Levels are:
        * 0: Debug
        * 1: Info
        * 2: Warning
        * 3: Errors
        * 4: Critical
        * 5: Quiet (nothing to print)

        By default, only display Info and higher. Don't input level > 5

        Args:
            level (int, optional): Level of verbosity of the message.
            Defaults to 2.
        """
        if level < 5 and level >= self.loglevel:
            print(message)

    def _change_page(self, url):
        """Change page, with side methods."""
        self._print("Changing page to {}".format(url), 0)
        self.page = self.session.get(url)
        # self.check_captcha()

    def get_page_meta(self) -> dict:
        """Retrieve metadata from the current self.page.



        Returns:
            dict: dictionary of all relevant metadata
        """
        # default case
        text = self.page.text
        meta = dict(re.findall(r'type="hidden" id="([^"]*)" value="([^"]*)"',
                               text))
        # if javascript was correctly loaded, look for injected metadata
        meta2_match = re.search("window.__data__ = ({(?:.*\n)*});",
                                self.page.text)
        if meta2_match is not None:
            try:
                meta2 = demjson.decode(meta2_match.group(1))
            except demjson.JSONDecodeError:
                self._print("[WARNING] Error with the meta parsing. This "
                            "should not be critical. Please contact a dev.", 2)
            meta.update(meta2)
        else:
            self._print("Advanced meta failed", 2)
            # self._print(self.page.text)
        self._print("Metas are {}".format(meta), 0)
        if len(meta) == 0:
            self._print("Unable to gather metadata in page")
            return None

        if "viewMp4Url" not in meta:
            self._print("No video URL in meta, going bruteforce", 2)
            vid_url_match = re.search((r"source src=[\"']"
                                       "(https?://ssrweb[^\"']+)[\"']"),
                                      text)
            if vid_url_match is None:
                self._print("[ERROR] Video not found in page. "
                            "Is it login-protected? ", 4)
                self._print(
                    "Try to refresh the webpage, and export cookies again", 4)
                return None
            meta["url"] = vid_url_match.group(1)
        return meta

    def download_vid(self, fname, clip=None):
        """Download one recording, and save it at fname."""
        self._print("Downloading filename {}, clip={}".format(
            fname, str(clip)), 0)
        all_urls = {self.metadata.get("viewMp4Url"),
                    self.metadata.get("url"),
                    self.metadata.get("shareMp4Url")}
        for ign in ["", None]:
            try:
                all_urls.remove(ign)
            except KeyError:
                pass
        if len(all_urls) > 1:
            self._print("Found {} screens, downloading all of them".format(len(all_urls)),
                        1)
            self._print(all_urls, 0)
        for vid_num, vid_url in enumerate(all_urls):
            extension = vid_url.split("?")[0].split("/")[-1].split(".")[1]
            name = (self.metadata.get("topic") or
                    self.metadata.get("r_meeting_topic")).replace(" ", "_")
            if (self.args.filename_add_date and
                    self.metadata.get("r_meeting_start_time")):
                name = name + "-" + \
                    self.metadata.get("r_meeting_start_time").replace(" ", "_")
            self._print("Found name is {}, extension is {}"
                        .format(name, extension), 0)
            if len(all_urls) > 1:
                name += f"_screen{vid_num}"
            filepath = get_filepath(fname, name, extension, clip)
            filepath_tmp = filepath + ".part"
            self._print("Full filepath is {}, temporary is {}".format(
                filepath, filepath_tmp), 0)
            self._print("Downloading '{}'...".format(
                filepath.split("/")[-1]), 1)
            vid_header = self.session.head(vid_url)
            total_size = int(vid_header.headers.get('content-length'))
            # unit_int, unit_str = ((1024, "KiB") if total_size < 30*1024**2
            #                       else (1024**2, "MiB"))
            start_bytes = int(os.path.exists(filepath_tmp) and
                              os.path.getsize(filepath_tmp))
            if start_bytes > 0:
                self._print("Incomplete file found ({:.2f}%), resuming..."
                            .format(100*start_bytes/total_size), 1)
            headers = {"Range": "bytes={}-".format(start_bytes)}
            vid = self.session.get(vid_url, headers=headers, stream=True)
            if vid.status_code in [200, 206] and total_size > 0:
                with open(filepath_tmp, "ab") as f, tqdm(total=total_size,
                                                         unit='B',
                                                         initial=start_bytes,
                                                         dynamic_ncols=True,
                                                         unit_scale=True,
                                                         unit_divisor=1024) as pbar:
                    for data in vid.iter_content(1024):
                        if data:
                            pbar.update(len(data))
                            f.write(data)
                            f.flush()
                self._print("Done!", 1)
                os.rename(filepath_tmp, filepath)
            else:
                self._print(
                    "Woops, error downloading: '{}'".format(vid_url), 3)
                self._print("Status code: {}, file size: {}".format(
                    vid.status_code, total_size), 0)
                sys.exit(1)

    def download(self, all_urls):
        """Exposed class to download a list of urls."""
        for url in all_urls:
            self.url = url
            try:
                regex = r"(?:https?:\/\/)?([^.]*\.?)(zoom[^.]*\.(?:us|com))"
                self.subdomain, self.domain = re.findall(regex, self.url)[0]
            except IndexError:
                self._print("Unable to extract domain and subdomain "
                            "from url {}, exitting".format(self.url), 4)
                sys.exit(1)
            self.session.headers.update({
                # set referer
                'referer': "https://{}{}/".format(self.subdomain,
                                                  self.domain),
            })
            if self.args.user_agent is None:
                if self.args.filename_add_date:
                    self._print("Forcing custom UA to have the date")
                    # if date is required, need invalid UA
                    # 'invalid' User-Agent
                    ua = "ZoomDL http://github.com/battleman/zoomdl"
                else:
                    self._print("Using standard Windows UA")
                    # somehow standard User-Agent
                    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/74.0.3729.169 Safari/537.36")
            else:
                ua = self.args.user_agent

            self.session.headers.update({
                "User-Agent": ua
            })
            self._change_page(url)
            if self.args.password is not None:
                self.authenticate()
            self.metadata = self.get_page_meta()
            if self.metadata is None:
                self._print("Unable to find metadata, aborting.", 4)
                return None

            # look for clips
            total_clips = int(self.metadata["totalClips"])
            current_clip = int(self.metadata["currentClip"])
            count_clips = self.args.count_clips
            filename = self.args.filename
            if count_clips == 1:  # only download this
                self.download_vid(filename)
            else:  # download multiple
                if count_clips == 0:
                    to_download = total_clips  # download this and all nexts
                else:  # download as many as asked (or possible)
                    to_download = min(count_clips, total_clips)
                for clip in range(current_clip, to_download+1):
                    self.download_vid(filename, clip)
                    url = self.page.url
                    next_time = str(self.metadata["nextClipStartTime"])
                    if next_time != "-1":
                        if "&startTime" not in url:
                            url += "&startTime={}".format(next_time)
                        else:
                            curr_time = re.findall(r"startTime=(\d+)", url)[0]
                            url = url.replace(curr_time, next_time)
                        self._change_page(url)
                        self.metadata = self.get_page_meta()

    def check_captcha(self):
        """Check whether or not a page is protected by CAPTCHA.

        TO BE IMPLEMENTED!!
        """
        self._print("Checking CAPTCHA", 0)
        captcha = False  # FIXME
        if captcha:
            self._print("The page {} is captcha-protected. Unable to download"
                        .format(self.page.url))
            sys.exit(1)

    def authenticate(self):
        # that shit has a password
        # first look for the meet_id
        self._print("Using password '{}'".format(self.args.password))
        meet_id_regex = re.compile("<input[^>]*")
        input_tags = meet_id_regex.findall(self.page.text)
        meet_id = None
        for inp in input_tags:
            input_split = inp.split()
            if input_split[2] == 'id="meetId"':
                meet_id = input_split[3][7:-1]
                break
        if meet_id is None:
            self._print("[CRITICAL]Unable to find meetId in the page",
                        4)
            if self.loglevel > 0:
                self._print("Please re-run with option -v 0 "
                            "and report it "
                            "to http://github.com/battleman/zoomdl",
                            4)
            self._print("\n".join(input_tags), 0)
            sys.exit(1)
        # create POST request
        data = {"id": meet_id, "passwd": self.args.password,
                "action": "viewdetailpage"}
        check_url = ("https://{}{}/rec/validate_meet_passwd"
                     .format(self.subdomain, self.domain))
        self.session.post(check_url, data=data)
        self._change_page(self.url)  # get as if nothing


def confirm(message: str):
    """
    Ask user to enter Y or N (case-insensitive).

    Inspired and adapted from
    https://gist.github.com/gurunars/4470c97c916e7b3c4731469c69671d06

    `return` {bool} True if the answer is Y.
    """
    answer = None
    while answer not in ["y", "n", ""]:
        answer = input(message + " Continue? [y/N]: ").lower()  # nosec
    return answer == "y"


def get_filepath(user_fname: Optional[str], file_fname: str, extension: str, clip=None):
    """Create an filepath."""

    if user_fname is None:
        basedir = os.getcwd()
        # remove illegal characters
        name = os.path.join(basedir,
                            re.sub(r"[/\\\?*:\"|><]+", "_", file_fname))

    else:
        name = os.path.abspath(user_fname)
    if clip is not None:
        name += "_clip{}".format(clip)
    filepath = "{}.{}".format(name, extension)
    # check file doesn't already exist
    if os.path.isfile(filepath):
        if not confirm("File {} already exists. This will erase it"
                       .format(filepath)):
            sys.exit(0)
        os.remove(filepath)
    return filepath
