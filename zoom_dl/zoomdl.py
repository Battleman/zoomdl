#/usr/bin/env python3
import sys
import os
# import requests
import re


def zoomdl(url, fname=None, password=None):
    session = requests.session()
    page = session.get(url)
    domain_re = re.compile("https://([^.]*)\.?zoom.us")
    domain = domain_re.match(url).group(1)
    session.headers.update(
            {'referer': "https://{}.zoom.us/".format(domain)})  # IMPORTANT
    if fname is not None:
        if fname[0] != "/":
            # asserting relative name
            fname = os.getcwd()+"/"+fname

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
        check_url = "https://{}.zoom.us/rec/validate_meet_passwd".format(domain)
        session.post(check_url, data=data)
        page = session.get(url)  # get as if nothing

    url_regexp = re.compile('http.*ssrweb.zoom.us[^\"]*')
    match = url_regexp.search(page.text)
    if match is None:
        print("Unable to open url {}. Are you sure there is no password, or have you entered it correctly?".format(url))
        sys.exit(1)
    vid_url = match.group()
    name, extension = vid_url.split("?")[0].split("/")[-1].split(".")
    if fname is not None:
        if fname[0] == "/":
            # absolute path is provided, keep as is
            name = fname
        else:
            # path probably is relative
            name = os.getcwd() + "/" + fname
    else:
        name = os.getcwd() + "/" + name
    print("Downloading...")
    vid = session.get(vid_url, cookies=session.cookies, stream=True)
    if vid.status_code == 200:
        with open("{}.{}".format(name, extension), "wb") as f:
            for chunk in vid:
                f.write(chunk)
        print("Done!")
    else:
        print("Woops, error downloading: '{}'".format(url))
        sys.exit(1)