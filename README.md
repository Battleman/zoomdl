# ZoomDL
## Goal
Conferences, meetings and presentations held on Zoom are often recorder and stored in the cloud, for a finite amount of time. The host can chose to make them available to download, but it is not mandatory.

Nonetheless, I believe if you can view it, you can download it. This script makes it easy to download any video stored on the Zoom Cloud. You just need to provide a valid zoom record URL, and optionally a filename, and it will download the file.

## Availability
The script was developed and tested under GNU/Linux (precisely, Debian 10). Thus, it should work for about any GNU/Linux distro out there, with common settings. You basically only need Python3 in your path.

Because it's Python, it will _probably_ work under OSX, and _may_ work under Windows. If it doesn't, you can report it as an issue, but honestly I don't know much about Windows and OSX.

## Installation
Nothing to install, just download the script and run it. If you wish to make it available system-wide, you can copy it to `/usr/local/bin/` (or anywhere else available in your PATH). Then you can simply use it wherever you want.

## Validity of urls
There are 2 type of valid urls.
* Those starting with _https://zoom.us/rec/play/..._
* Or, with a domain, _https://X.zoom.us/rec/play/..._ where _X_ is a domain, something like _us02web_, _epfl_,... or similar.

If there is a domain in your url, make sure to include it, it's crucial.
## Usage
`zoomdl [-h] -u/--url "url" [-f/--fname "filename"] [-p/--password "password"]`
* `-u/--url` is mandatory, it represents the URL of the video
* `-f/--fname` is optional, it is the name of the resulting file _without extension_. If nothing is provided, the default name given by Zoom will be used. Extension (`.mp4`, `.mkv`,... is automatic)
* `-p/--password` is too optional. Set it when your video has a password.

The quotes are not mandatory, but if your filename/url/password/... contains reserved characters (`\`, `&`, `$`,`%`...), quotes are the way to go.
## Requirements
All dependencies are bundled within the executable. This allows to make a standalone execution without need for external libraries.

If you wish to build it yourself, see `requirements.txt`. The most important requirement is [requests](https://github.com/psf/requests). Please see [acknowledgements](#acknowledgements) for a note on that.

## Acknowledgements
The folder executable contains [requests](https://github.com/psf/requests) (and its dependencies), an awesome wrapper for HTTP(s) calls. Please check them out!

## Support
Like this project? Consider supporting me, for more awesome updates

<a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/Battleman"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:15px;font-size:28px !important;">Buy me a coffee</span></a>
