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
        # "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        #                "AppleWebKit/537.36 (KHTML, like Gecko) "
        #                "Chrome/74.0.3729.169 "
        #                "Safari/537.36")  # somehow standard User-Agent
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0"
    })

    if args.password is not None:
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

    metadata = get_meta(page.text)
    total_clips = metadata["totalClips"]
    current_clip = metadata["currentClip"]
    count_clips = args.count_clips
    filename = args.filename
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
            nextTime = metadata["nextClipStartTime"]
            currTime = metadata["clipStartTime"]
            if currTime in url:
                url = url.replace(currTime, nextTime)
            else:
                url += "&startTime={}".format(nextTime)
            page = session.get(url)


def get_meta(text):
    """Get metadata by trying multiple ways."""
    # default case
    meta = dict(re. findall('id="([^"]*)" value="([^"]*)"', text))
    # if javascript was correctly loaded
    meta2 = dict(re.findall("\s?(\w+): [\"' ]*([^\"',]*)[\"' ]*,", text))
    meta.update(meta2)
    if len(meta) == 0:
        print("Unable to gather metadata in page")
        return None
    if "viewMp4Url" not in meta:
        vid_url = re.search("source src=[\"'](https?://ssrweb[^\"']+)[\"']",
                            text).group(1)
        meta["url"] = vid_url
    return meta


def download_vid(page, session, fname, clip=None):
    metadata = get_meta(page.text)
    vid_url = metadata.get("viewMp4Url") or metadata.get("url")
    extension = vid_url.split("?")[0].split("/")[-1].split(".")[1]
    name = (metadata.get("topic") or metadata.get(
        "r_meeting_topic")).replace(" ", "_")
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
