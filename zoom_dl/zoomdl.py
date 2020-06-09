#!/usr/bin/env python3
import sys
import os
import requests
import re
import platform


def zoomdl(url, fname=None, password=None):
    session = requests.session()
    page = session.get(url)
    domain_re = re.compile("https://([^.]*\.?)zoom.us")
    domain = domain_re.match(url).group(1)
    session.headers.update(
        {'referer': "https://{}zoom.us/".format(domain)})  # IMPORTANT

    if password is not None:
        # that shit has a password
        # first look for the meet_id
        meet_id_regex = re.compile("<input[^>]*")
        for inp in meet_id_regex.findall(page.text):
            input_split = inp.split()
            if input_split[2] == 'id="meetId"':
                meet_id = input_split[3][7:-1]
                break
        # create POST request
        data = {"id": meet_id, "passwd": password, "action": "viewdetailpage"}
        check_url = "https://{}zoom.us/rec/validate_meet_passwd".format(
            domain)
        session.post(check_url, data=data)
        page = session.get(url)  # get as if nothing

    url_regexp = re.compile('http.*ssrweb.zoom.us[^\"]*')
    match = url_regexp.search(page.text)
    if match is None:
        print("Unable to open url {}. Are you sure there is no password, or have you entered it correctly?".format(url))
        sys.exit(1)
    vid_url = match.group()
    name, extension = vid_url.split("?")[0].split("/")[-1].split(".")

    filepath = get_filepath(fname, name, extension)

    print("Downloading...")
    vid = session.get(vid_url, cookies=session.cookies, stream=True)
    if vid.status_code == 200:
        with open(filepath, "wb") as f:
            for chunk in vid:
                f.write(chunk)
        print("Done!")
    else:
        print("Woops, error downloading: '{}'".format(url))
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
        if not confirm("File {} already exists. This will erase it".format(filepath)):
            print("Aborting")
            sys.exit(0)
    return filepath
