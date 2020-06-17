#!/usr/bin/env python3
import sys
import os
import requests
import re


def zoomdl(args):
    session = requests.session()
    url = args.url
    page = session.get(url)
    domain_re = re.compile("https://([^.]*\.?)zoom.us")
    domain = domain_re.match(url).group(1)
    session.headers.update({
        'referer': "https://{}zoom.us/".format(domain),  # set referer
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/74.0.3729.169 "
                       "Safari/537.36")  # somehow standard User-Agent
    })

    if "password" in args:
        # that shit has a password
        # first look for the meet_id
        meet_id_regex = re.compile("<input[^>]*")
        for inp in meet_id_regex.findall(page.text):
            input_split = inp.split()
            if input_split[2] == 'id="meetId"':
                meet_id = input_split[3][7:-1]
                break

        # create POST request
        data = {"id": meet_id, "passwd": args.password,
                "action": "viewdetailpage"}
        check_url = "https://{}zoom.us/rec/validate_meet_passwd".format(
            domain)
        session.post(check_url, data=data)
        page = session.get(url)  # get as if nothing

    total_clips = get_meta("totalClips", page.text, int)
    current_clip = get_meta("currentClip", page.text, int)
    count_clips = args.count_clips
    filename = None if "filename" not in args else args.filename
    if count_clips == 1:  # only download this
        download_vid(page, session, filename)
    else:  # download multiple
        if count_clips == 0:
            to_download = total_clips  # download this and nexts
        else:  # download as many as asked (or possible)
            to_download = min(count_clips, total_clips)
        for clip in range(current_clip, to_download+1):
            download_vid(page, session, filename, clip)
            url = page.url
            nextTime = get_meta("nextClipStartTime", page.text)
            currTime = get_meta("clipStartTime", page.text)
            if currTime in url:
                url = url.replace(currTime, nextTime)
            else:
                url += "&startTime={}".format(nextTime)
            page = session.get(url)


def get_meta(field, text, ret_type=str):
    search = re.search("{}: ['\"]?([^\"',]+)['\"]?".format(field), text)
    if search is None:
        print("Unable to find {} in page".format(field))
        return None
    else:
        return ret_type(search.group(1))




def download_vid(page, session, fname, clip=None):
    vid_url = get_meta("viewMp4Url", page.text)
    extension = vid_url.split("?")[0].split("/")[-1].split(".")[1]
    name = get_meta("topic", page.text).replace(" ", "_")
    name = name if clip is None else "{}-{}".format(name, clip)
    filepath = get_filepath(fname, name, extension)
    if filepath is None:
        return
    print("Downloading '{}'...".format(filepath.split("/")[-1]))
    vid = session.get(vid_url, cookies=session.cookies, stream=True)
    if vid.status_code == 200:
        with open(filepath, "wb") as f:
            for chunk in vid:
                f.write(chunk)
        print("Done!")
    else:
        print("Woops, error downloading: '{}'".format(vid_url))
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
        answer = input(message + " Continue? [y/N]: ").lower()
    return answer == "y"


def get_filepath(user_fname, file_fname, extension):
    """Create an filepath."""
    if user_fname is None:
        basedir = os.getcwd()
        name = os.path.join(basedir, file_fname)
    else:
        name = os.path.abspath(user_fname)
    filepath = "{}.{}".format(name, extension)
    # check file doesn't already exist
    if os.path.isfile(filepath):
        if not confirm("File {} already exists. This will erase it"
                       .format(filepath)):
            return None
    return filepath
