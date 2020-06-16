# ZoomDL

## Support
Like this project? Consider supporting me, for more awesome updates

<a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/Battleman"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:15px;font-size:28px !important;">Buy me a coffee</span></a>

## Goal
Conferences, meetings and presentations held on Zoom are often recorded and stored in the cloud, for a finite amount of time. The host can chose to make them available to download, but it is not mandatory.

Nonetheless, I believe if you can view it, you can download it. This script makes it easy to download any video stored on the Zoom Cloud. You just need to provide a valid zoom record URL, and optionally a filename, and it will download the file.

## Availability
The script was developed and tested under GNU/Linux (precisely, Debian 10). Thus, it should work for about any GNU/Linux distro out there, with common settings. You basically only need Python3 in your path.

*New from 2020.06.09* There now exists an executable file `zoomdl.exe` for Windows. It was kinda tested under Windows 10. Because I never coded under Windows, I have very few tests, mostly empirical ones. Expect bugs! If you encounter a Windows-specific error, don't expect much support. If the error is related to the general logic of the program, report it and I'll do my best to fix it.

## Installation
### Linux/OSX
You need to have a valid Python3 installation. Except from that, just download the script `zoomdl` (not `zoomdl.exe`) and run it like a normal binary. If you wish to make it available system-wide, you can copy it to `/usr/local/bin/` (or anywhere else available in your PATH). Then you can simply use it wherever you want.
### Windows
**This is still in beta**
Grab the dedicated binary `zoomdl.exe`, and launch it using your command line. If you don't know how, visit [this wikihow](https://www.wikihow.com/Run-an-EXE-File-From-Command-Prompt). You may encounter warning from your anti-virus, you can ignore them (I'm not evil, pinky-promise). You probably don't need a Python3 installation, it *should* be contained within the executable.

## Validity of urls
There are 2 type of valid urls.
* Those starting with _https://zoom.us/rec/play/..._
* Or, with a domain, _https://X.zoom.us/rec/play/..._ where _X_ is a domain, something like _us02web_, _epfl_,... or similar.

If there is a domain in your url, make sure to include it, it's crucial.
## Usage
`zoomdl [-h] -u/--url "url" [-f/--fname "filename"] [-p/--password "password"] [-c/--count-clips count]`
* `-u/--url` is mandatory, it represents the URL of the video
* `-f/--fname` is optional, it is the name of the resulting file _without extension_. If nothing is provided, the default name given by Zoom will be used. Extension (`.mp4`, `.mkv`,... is automatic)
* `-p/--password` is too optional. Set it when your video has a password.
* `-c/--count-clips`: Sometimes, one URL can contain multiple clips. This tunes the number of clips that will be downloaded. Recordings with multiple clips seem to be quite rare, but do exist. The parameter `count` works as follow:
  * 0 means: download all of them (starting from the current clip)
  * 1 means: download only the first/given clip
  * \> 1 means: download until you reach this number of clip (or the end)


### About quotes [IMPORTANT]
The quotes are not mandatory, but if your filename/url/password/... contains reserved characters (`\`, `&`, `$`,`%`...), quotes are the way to go.

Under Linux/OSX, it is strongly advised to use *single quotes*, because `"4$g3.2"` will replace `$g3` by nothing, while `'4$g3.2'` will leave the string as-is.

Under Windows, I *think* you must use double quotes everywhere. Don't quote me on that.


## Requirements
All dependencies are bundled within the executable. This allows to make a standalone execution without need for external libraries.

If you wish to build it yourself, see `requirements.txt`. The most important requirement is [requests](https://github.com/psf/requests). Please see [acknowledgements](#acknowledgements) for a note on that.

## Acknowledgements
The folder executable contains [requests](https://github.com/psf/requests) (and its dependencies), an awesome wrapper for HTTP(s) calls. Please check them out!
