#!/usr/bin/env python3
# coding: utf-8
"""Define the main ZoomDL class and its methods."""
import sys
import os
import requests
import re
from tqdm import tqdm
import demjson
# import browser_cookie3


class ZoomDL():
    """Class for ZoomDL."""

    def __init__(self, args):
        """Init the class."""
        self.args = args
        self.session = requests.session()
        self.loglevel = self.args.log_level
        # self._set_cookies(self.args.browser)

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

    # def _set_cookies(browser):
    #     if browser is None:
    #         pass
    #     else:
    #         if browser.lower == "firefox":
    #             self.session.cookies = browser_cookie3.firefox()
    #         elif browser.lower == "chrome":
    #             self.session.cookies = browser_cookie3.chrome()
    #         else:
    #             raise ValueError(("Browser {} not understood; "
    #                               "Use Firefox or Chrome").format(browser))

    def _change_page(self, url):
        """Change page, with side methods."""
        self._print("Changing page to {}".format(url), 0)
        self.page = self.session.get(url)
        self.check_captcha()

    def get_page_meta(self):
        """Get metadata by trying multiple ways."""
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
                return None
            meta["url"] = vid_url_match.group(1)
        return meta

    def download_vid(self, fname, clip=None):
        """Download one recording, and save it at fname."""
        vid_url = self.metadata.get("viewMp4Url") or self.metadata.get("url")
        extension = vid_url.split("?")[0].split("/")[-1].split(".")[1]
        name = (self.metadata.get("topic") or
                self.metadata.get("r_meeting_topic")).replace(" ", "_")
        if (self.args.filename_add_date and
                self.metadata.get("r_meeting_start_time")):
            name = name + "-" + self.metadata.get("r_meeting_start_time")
        self._print("Found name is {}, extension is {}"
                    .format(name, extension), 0)
        name = name if clip is None else "{}-{}".format(name, clip)
        filepath = get_filepath(fname, name, extension)
        if filepath is None:
            self._print("Filepath is none, interrupting")
            return
        self._print("Full filepath is {}".format(filepath), 0)
        self._print("Downloading '{}'...".format(filepath.split("/")[-1]), 1)
        vid = self.session.get(vid_url, stream=True)
        if vid.status_code == 200:
            with open(filepath, "wb") as f:
                total_size = int(vid.headers.get('content-length'))
                unit_int, unit_str = ((1024, "KiB") if total_size < 30*1024**2
                                      else (1024**2, "MiB"))
                for chunk in tqdm(vid.iter_content(chunk_size=unit_int),
                                  total=total_size//unit_int + 1,
                                  unit=unit_str, mininterval=0.2,
                                  dynamic_ncols=True):
                    if chunk:
                        f.write(chunk)
                        f.flush()
            self._print("Done!", 1)
        else:
            self._print("Woops, error downloading: '{}'".format(vid_url), 3)
            self._print("Status code: {}".format(vid.status_code), 0)
            sys.exit(1)

    def download(self, all_urls):
        """Exposed class to download a list of urls."""
        for url in all_urls:
            domain = re.match(r"https?://([^.]*\.?)zoom.us", url).group(1)
            self.session.headers.update({
                'referer': "https://{}zoom.us/".format(domain),  # set referer
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
                # that shit has a password
                # first look for the meet_id
                self._print("Using password '{}'".format(self.args.password))
                meet_id_regex = re.compile("<input[^>]*")
                for inp in meet_id_regex.findall(self.page.text):
                    input_split = inp.split()
                    if input_split[2] == 'id="meetId"':
                        meet_id = input_split[3][7:-1]
                        break

                # create POST request
                data = {"id": meet_id, "passwd": self.args.password,
                        "action": "viewdetailpage"}
                check_url = ("https://{}zoom.us/rec/validate_meet_passwd"
                             .format(domain))
                self.session.post(check_url, data=data)
                self._change_page(url)  # get as if nothing

            self.metadata = self.get_page_meta()
            if self.metadata is None:
                self._print("Unable to find metadata, aborting.", 4)
                return None
            total_clips = self.metadata["totalClips"]
            current_clip = self.metadata["currentClip"]
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
                    nextTime = str(self.metadata["nextClipStartTime"])
                    currTime = str(self.metadata["clipStartTime"])
                    if currTime in url:
                        url = url.replace(currTime, nextTime)
                    else:
                        url += "&startTime={}".format(nextTime)
                    self._change_page(url)

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


def confirm(message):
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


def get_filepath(user_fname, file_fname, extension):
    """Create an filepath."""

    if user_fname is None:
        basedir = os.getcwd()
        # remove illegal characters
        name = os.path.join(basedir, re.sub("[/\\\?*:\"|><]+", "_", file_fname))

    else:
        name = os.path.abspath(user_fname)
    filepath = "{}.{}".format(name, extension)
    # check file doesn't already exist
    if os.path.isfile(filepath):
        if not confirm("File {} already exists. This will erase it"
                       .format(filepath)):
            return None
    return filepath
