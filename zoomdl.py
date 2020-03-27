import sys
import argparse
try:
    import requests
except ModuleNotFoundError:
    print("Module 'requests' required. Install it with 'pip install requests' or 'conda install requests'")
    sys.exit(1)
import re


def main(url, fname=None):
    page = requests.get(url)
    cookies = page.cookies

    url_regexp = re.compile('https.*ssrweb.zoom.us[^\"]*')
    vid_url = url_regexp.search(page.text)[0]
    name, extension = vid_url.split("?")[0].split("/")[-1].split(".")
    if fname is not None:
        name = fname
    print("Downloading...")
    vid = requests.get(vid_url, cookies=cookies, stream=True)
    if vid.status_code == 200:
        with open("{}.{}".format(name, extension), "wb") as f:
            for chunk in vid:
                f.write(chunk)
    print("Done!")


if __name__ == "__main__":
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
                        help="The name of the output video file. Default to the filename according to Zoom",
                        metavar="filename")
    args = PARSER.parse_args()
    main(args.url, args.filename)
