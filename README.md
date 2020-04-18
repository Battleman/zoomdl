# ZoomDL
## Goal
Conferences, meetings and presentations held on Zoom are often recorder and stored in the cloud, for a finite amount of time. The host can chose to make them available to download, but it is not mandatory. 

Nonetheless, I believe if you can view it, you can download it. This script makes it easy to download any video stored on the Zoom Cloud. You just need to provide a zoom record URL (starting with _zoom.us/rec/play/..._), and optionally a filename, and it will download the file.

## Installation
Nothing to install, just download the script and run it.

## Usage
`python [-h] -u/--url url [-f/--fname filename]`
* `-u/--url` is mandatory, it represents the URL of the video
* `-f/--fname` is optional, it is the name of the resulting file _without extension_. If nothing is provided, the default name given by Zoom will be used. Extension (`.mp4`, `.mkv`,... is automatic)
* `-p/--password` is too optional. Set it when your video has a password.

## Requirements
Only very standard modules are necessary: `requests`, `re`, `argparse` and `sys`. The 3 latter should be included in any python distribution, while the former is standard, and easy to install (try `pip install requests` or `conda install requests`).

## Support
Like this project? Consider supporting me, for more awesome updates

<a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/Battleman"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:15px;font-size:28px !important;">Buy me a coffee</span></a>
