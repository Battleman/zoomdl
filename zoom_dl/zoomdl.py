#!/usr/bin/env python3
# coding: utf-8
"""Define the main ZoomDL class and its methods."""
import os
import re
import sys

import demjson3
import requests
from tqdm import tqdm
from typing import Optional
import datetime
import json

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

    @property
    def recording_name(self):
        """Return name of the current recording."""
        name = (self.metadata.get("topic") or
                self.metadata.get("r_meeting_topic")).replace(" ", "_")
        if self.args.filename_add_date:
            recording_start_time = datetime.datetime.fromtimestamp(
                self.metadata["fileStartTime"] / 1000)
            name = name + "_" + recording_start_time.strftime("%Y-%m-%d")
        return name

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

    def get_page_meta(self) -> Optional[dict]:
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
                meta2 = demjson3.decode(meta2_match.group(1))
            except demjson3.JSONDecodeError:
                self._print("[WARNING] Error with the meta parsing. This "
                            "should not be critical. Please contact a dev.", 2)
            meta.update(meta2)
        else:
            self._print("Advanced meta failed", 2)
            # self._print(self.page.text)

        # look for injected chat messages
        chats = []
        chat_match = re.findall(
            r"window.__data__.chatList.push\(\s*?({(?:.*\n)*?})\s*?\)",
            self.page.text)
        if len(chat_match) > 0:
            for matched_json in chat_match:
                try:
                    message = demjson3.decode(matched_json)
                    chats.append(message)
                except demjson3.JSONDecodeError:
                    self._print("[WARNING] Error with the meta parsing. This "
                                "should not be critical. "
                                "Please contact a dev.", 2)
        else:
            self._print("Unable to extract chatList from page", 0)
        meta["chatList"] = chats

        # look for injected transcripts
        transcripts = []
        transcript_match = re.findall(
            r"window.__data__.transcriptList.push\(\s*?({(?:.*\n)*?})\s*?\)",
            self.page.text)
        if len(transcript_match) > 0:
            for matched_json in transcript_match:
                try:
                    message = demjson3.decode(matched_json)
                    transcripts.append(message)
                except demjson3.JSONDecodeError:
                    self._print("[WARNING] Error with the meta parsing. This "
                                "should not be critical. "
                                "Please contact a dev.", 2)
        else:
            self._print("Unable to extract transcriptList from page", 0)
        meta["transcriptList"] = transcripts

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

    def dump_page_meta(self, fname, clip: int = None):
        """
        Dump page meta in json format to fname.
        """
        self._print("Dumping page meta...", 0)
        filepath = get_filepath(fname, self.recording_name, "json", clip)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f)
        self._print(f"Dumped page meta to '{filepath}'.", 1)

    def download_vid(self, fname, clip: int = None):
        """Download one recording and save it at fname.

        Including videos, chat, and transcripts
        """
        self._print("Downloading filename {}, clip={}".format(
            fname, str(clip)), 0)
        all_urls = {
            "camera": self.metadata.get("viewMp4Url"),
            "screen": self.metadata.get("shareMp4Url"),
            # the link below is rarely valid
            # (only when both the two links above are invalid)
            "unknown": self.metadata.get("url"),
        }
        for key, url in all_urls.copy().items():
            if url is None or url == "":
                all_urls.pop(key)
        if len(all_urls) > 1:
            self._print((f"Found {len(all_urls)} screens, "
                         "downloading all of them"),
                        1)
            self._print(all_urls, 0)

        for vid_name, vid_url in all_urls.items():
            extension = vid_url.split("?")[0].split("/")[-1].split(".")[1]
            self._print("Found name is {}, vid_name is {}, extension is {}"
                        .format(self.recording_name, vid_name, extension), 0)
            vid_name_appendix = f"_{vid_name}" if len(all_urls) > 1 else ""
            filepath = get_filepath(
                fname, self.recording_name, extension, clip, vid_name_appendix)
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
                with open(filepath_tmp, "ab") as vid_file:
                    with tqdm(total=total_size,
                              unit='B',
                              initial=start_bytes,
                              dynamic_ncols=True,
                              unit_scale=True,
                              unit_divisor=1024) as pbar:
                        for data in vid.iter_content(1024):
                            if data:
                                pbar.update(len(data))
                                vid_file.write(data)
                                vid_file.flush()
                self._print("Done!", 1)
                os.rename(filepath_tmp, filepath)
            else:
                self._print(
                    "Woops, error downloading: '{}'".format(vid_url), 3)
                self._print("Status code: {}, file size: {}".format(
                    vid.status_code, total_size), 0)
                sys.exit(1)

        # save chat
        if self.args.save_chat is not None:
            messages = self.metadata["chatList"]
            if len(messages) == 0:
                self._print(f"Unable to retrieve chat message from url"
                            f" {self.url} (is there no chat message?)", 2)
            else:
                # Convert time string to proper format
                for message in messages:
                    message["time"] = shift_time_delta(message["time"])

                if self.args.save_chat == "txt":
                    chat_filepath = get_filepath(
                        fname, self.recording_name, "txt", clip, ".chat")
                    with open(chat_filepath, "w", encoding="utf-8") as outfile:
                        for idx, message in enumerate(messages):
                            outfile.write("[{}] @ {} :\n".format(
                                message["username"], message["time"]))
                            outfile.write(message["content"] + "\n")
                            if idx + 1 < len(messages):
                                outfile.write("\n")
                elif self.args.save_chat == "srt":
                    chat_filepath = get_filepath(
                        fname, self.recording_name, "srt", clip, ".chat")
                    with open(chat_filepath, "w", encoding="utf-8") as outfile:
                        for idx, message in enumerate(messages):
                            end_time = shift_time_delta(
                                message["time"], self.args.chat_subtitle_dur)
                            outfile.write(str(idx+1) + "\n")
                            outfile.write(
                                f"{message['time']},000 --> {end_time},000\n")
                            outfile.write(message["username"] +
                                          ": " + message["content"] + "\n")
                            if idx + 1 < len(messages):
                                outfile.write("\n")
                self._print(
                    f"Successfully saved chat into '{chat_filepath}'!", 1)

        # save transcripts
        if self.args.save_transcript is not None:
            transcripts = self.metadata["transcriptList"]
            if len(transcripts) == 0:
                self._print("Unable to retrieve transcript from url"
                            f"{self.url} (is transcript not enabled "
                            "in this video?)", 2)
            else:
                if self.args.save_transcript == "txt":
                    tran_filepath: str = get_filepath(fname,
                                                      self.recording_name,
                                                      "txt",
                                                      clip,
                                                      ".transcript")
                    with open(tran_filepath, "w", encoding="utf-8") as outfile:
                        for idx, transcript in enumerate(transcripts):
                            outfile.write("[{}] @ {} --> {} :\n".format(
                                transcript["username"],
                                transcript["ts"],
                                transcript["endTs"]))
                            outfile.write(transcript["text"] + "\n")
                            if idx + 1 < len(transcripts):
                                outfile.write("\n")
                elif self.args.save_transcript == "srt":
                    tran_filepath = get_filepath(
                        fname, self.recording_name, "srt", clip, ".transcript")
                    with open(tran_filepath, "w", encoding="utf-8") as outfile:
                        for idx, transcript in enumerate(transcripts):
                            outfile.write(str(idx+1) + "\n")
                            outfile.write("{} --> {}\n".format(
                                transcript["ts"].replace(".", ","),
                                transcript["endTs"].replace(".", ",")))
                            outfile.write(transcript["username"] +
                                          ": " +
                                          transcript["text"] +
                                          "\n")
                            if idx + 1 < len(transcripts):
                                outfile.write("\n")
                self._print("Successfully saved transcripts "
                            f"into '{tran_filepath}'!", 1)

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
                self._print("Using standard Windows UA", 0)
                # somehow standard User-Agent
                ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/74.0.3729.169 Safari/537.36")
            else:
                ua = self.args.user_agent
                self._print("Using custom UA: " + ua, 0)

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
                if self.args.dump_pagemeta:
                    self.dump_page_meta(filename)
            else:  # download multiple
                if count_clips == 0:
                    to_download = total_clips  # download this and all nexts
                else:  # download as many as asked (or possible)
                    to_download = min(count_clips, total_clips)
                for clip in range(current_clip, to_download+1):
                    self.download_vid(filename, clip)
                    if self.args.dump_pagemeta:
                        self.dump_page_meta(filename, clip)
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

    # def check_captcha(self):
    #     """Check whether or not a page is protected by CAPTCHA.
    #     TO BE IMPLEMENTED!!
    #     """
    #     self._print("Checking CAPTCHA", 0)
    #     captcha = False  # FIXME
    #     if captcha:
    #         self._print((f"The page {self.page.url} is captcha-protected. "
    #         "Unable to download"))
    #         sys.exit(1)

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


def get_filepath(user_fname: str,
                 file_fname: str,
                 extension: str,
                 clip: int = None,
                 appendix: str = "") -> str:
    """Create an filepath."""
    if user_fname is None:
        basedir = os.getcwd()
        # remove illegal characters
        name = os.path.join(basedir, re.sub(
            r"[/\\\?*:\"|><]+", "_", file_fname))

    else:
        name = os.path.abspath(user_fname)
    if clip is not None:
        name += "_clip{}".format(clip)
    name += appendix
    filepath = "{}.{}".format(name, extension)
    # check file doesn't already exist
    if os.path.isfile(filepath):
        if not confirm("File {} already exists. This will erase it"
                       .format(filepath)):
            sys.exit(0)
        os.remove(filepath)
    return filepath


def shift_time_delta(time_str: str,
                     delta_second: int = 0,
                     with_ms: bool = False):
    """Shift given time by adding `delta_second` seconds then format it.

    `delta_seconds` can be negative.
    """
    tmp_timedelta = parse_timedelta(time_str)
    total_seconds = int(tmp_timedelta.total_seconds()) + delta_second
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    output = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    if with_ms:
        output += f'.{tmp_timedelta.microseconds:03d}'
    return output


def parse_timedelta(value):
    """
    Convert input string to timedelta.

    Supported strings are like `01:23:45.678`.
    """
    value = re.sub(r"[^0-9:.]", "", value)
    if not value:
        return
    if "." in value:
        ms = int(value.split(".")[1])
        value = value.split(".")[0]
    else:
        ms = 0
    delta = datetime.timedelta(**{
        key: float(val)
        for val, key in zip(value.split(":")[::-1],
                            ("seconds", "minutes", "hours", "days"))
    })
    delta += datetime.timedelta(microseconds=ms)
    return delta
