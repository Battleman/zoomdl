# ZoomDL

## Support
Like this project? Consider supporting me, for more awesome updates

<a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/Battleman"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:15px;font-size:28px !important;">Buy me a coffee</span></a>

## ANNOUNCEMENT LOOKING FOR TESTERS
More and more, I face the challenge of testing. I code on my own Debian machine, and use a Windows 10 VM to compile the executable. But testing has become more and more a challenge, especially for new features.

If you are anyhow interested in helping (there are various ways to!), go to the dedicated issue (#32), and comment there. The concept is still very young for me, sorry that.

- [ZoomDL](#zoomdl)
  - [Support](#support)
  - [ANNOUNCEMENT LOOKING FOR TESTERS](#announcement-looking-for-testers)
  - [Goal](#goal)
  - [Availability](#availability)
  - [Installation](#installation)
    - [Linux/OSX](#linuxosx)
    - [Windows](#windows)
  - [Usage](#usage)
    - [Cookies / SSO / Captcha / Login](#cookies--sso--captcha--login)
    - [About syntax](#about-syntax)
    - [About quotes [IMPORTANT]](#about-quotes-important)
    - [Validity of urls](#validity-of-urls)
  - [Building from sources](#building-from-sources)
    - [Linux](#linux)
    - [Windows](#windows-1)
  - [Requirements](#requirements)
  - [Acknowledgements](#acknowledgements)

## Goal
Conferences, meetings and presentations held on Zoom are often recorded and stored in the cloud, for a finite amount of time. The host can chose to make them available to download, but it is not mandatory.

Nonetheless, I believe if you can view it, you can download it. This script makes it easy to download any video stored on the Zoom Cloud. You just need to provide a valid zoom record URL, and optionally a filename, and it will download the file.

## Availability
The script was developed and tested under GNU/Linux (precisely, Debian 10). Thus, it should work for about any GNU/Linux distro out there, with common settings. You basically only need Python3 in your path.

*New from 2020.06.09* There now exists an executable file `zoomdl.exe` for Windows. It was kinda tested under Windows 10. Because I never coded under Windows, I have very few tests, mostly empirical ones. Expect bugs! If you encounter a Windows-specific error, don't expect much support. If the error is related to the general logic of the program, report it and I'll do my best to fix it.

## Installation
### Linux/OSX
You need to have a valid Python3 installation. Except from that, just download the script `zoomdl` (not `zoomdl.exe`) and run it like a normal binary. If you wish to make it available system-wide, you can copy it to `/usr/local/bin/` (or anywhere else available in your PATH). Then you can simply use it wherever you want.

The following two commands make that easy. In a terminal, run:
```bash
sudo wget https://github.com/Battleman/zoomdl/releases/latest/download/zoomdl -O /usr/bin/zoomdl
sudo chmod +x /usr/bin/zoomdl
```
You will be prompted to enter your password (your computer password, not zoom). It's likely that you won't see anything as you type it, don't worry, it [is normal](https://askubuntu.com/questions/112069/nothing-shows-up-in-the-terminal-when-i-type-my-password) ([even for OSX](https://osxdaily.com/2015/02/04/terminal-wont-show-password-when-typed/))

Once you have done that, you can use your terminal and type the commands normally.

### Windows
**This is still in beta**
Grab the dedicated binary `zoomdl.exe`, and launch it using your command line. If you don't know how, visit [this wikihow](https://www.wikihow.com/Run-an-EXE-File-From-Command-Prompt). You may encounter warning from your anti-virus, you can ignore them (I'm not evil, pinky-promise). You probably don't need a Python3 installation, it *should* be contained within the executable.

If there is a domain in your url, make sure to include it, it's crucial.
## Usage
`zoomdl [-h] -u/--url 'url' [-f/--fname 'filename'] [-p/--password 'password'] [-c/--count-clips count] [-d/--filename-add-date] [--user-agent 'custom_user_agent]`
* `-u/--url` is mandatory, it represents the URL of the video
* `-f/--fname` is optional, it is the name of the resulting file _without extension_. If nothing is provided, the default name given by Zoom will be used. Extension (`.mp4`, `.mkv`,... is automatic)
* `-p/--password` is too optional. Set it when your video has a password.
* `-c/--count-clips`: Sometimes, one URL can contain multiple clips. This tunes the number of clips that will be downloaded. Recordings with multiple clips seem to be quite rare, but do exist. The parameter `count` works as follow:
  * 0 means: download all of them (starting from the current clip)
  * 1 means: download only the first/given clip
  * \> 1 means: download until you reach this number of clip (or the end)
* `-d/--filename-add-date` will append the date of the recording to the filename. **without effect if `-f` is specified**
* `--user-agent` (no shorthand notation): lets you specify a custom User-Agent (only do that if you know what you're doing and why)
* `--cookies` (no shorthand notation): specify the path to a cookie jar file. 

### Cookies / SSO / Captcha / Login
Some videos are protected with more than a password. You require an SSO, or to solve a captcha. The `cookies` option allows you to perform all the steps in a browser, and then use the cookies to access the video. This functionality is similar to Youtube-dl's same option.

**Howto:**
1. (Only once, the first time) In your favourite browser (works for Firefox-based or Chrome-based), install a cookies-export extension. Cookies must some in the _Netscape format_. There are multiple extensions out there, chose your favourite. For example [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/), [Other Firefox](https://addons.mozilla.org/en-US/firefox/addon/export-cookies-txt/), [Chrome](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid), [Other Chrome](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
2. With the same browser, visit the video you want to download; pass all required verifications (SSO, captcha, login,...), until you are able to view the video
3. Using the aformentioned extension, export your cookies. You need the cookies for the domain (`.zoom.us`), so export at least "cookies for this site", or "cookies for this domain", or whatever it's called.
4. Save generated file somewhere (for example, `Downloads/cookies.txt`)
5. When calling ZoomDL, use the option `--cookies path/to/the/cookies.txt`

If you want to download several videos who use the same login (like SSO), you only need to export the cookies once

### About syntax
I see a lot of people who don't understand what the above means. Here is a short explanation:
* This is a _command_, with multiple possible _parameters_.
* Parameters usually have a short version (with one dash, like `-u`) and an equivalent long version (with two dashes, like `--url`); the short and long version are shown separated by a `/`; you must only use one of them.
* The parameters between square brackets are optional (like `-f`, that allows you to input a custom filename). The others (for the moment, only `-u`) are mandatory.
* The order of parameters don't matter
* the `-h` parameter only displays a short help and commands explanation

For example, those are all valid commands (ofc by replacing the URLs):
```
zoomdl -u 'https://my_url' -f "recording_from_monday"
zoomdl --url 'https://my_url'
zoomdl -p '$28fn2f8' --filename-add-date --filename "recording_from_tuesday" -u 'https://my_url' --user-agent "Windows 10 wonderful User-Agent" -v 3
```
### About quotes [IMPORTANT]
The quotes are not mandatory, but if your filename/url/password/... contains reserved characters (`\`, `&`, `$`,`%`...), quotes are the way to go.

Under Linux/OSX, it is strongly advised to use *single quotes*, because `"4$g3.2"` will replace `$g3` by nothing, while `'4$g3.2'` will leave the string as-is.

Under Windows, I *think* you must use double quotes everywhere. Don't quote me on that.

### Validity of urls
There are 3 type of valid urls.
* Those starting with _https://zoom.us/rec/play/..._
* Or, with a domain, _https://X.zoom.us/rec/play/..._ where _X_ is a domain, something like _us02web_, _epfl_,... or similar.
* Finally, governemantal urls: _https://X.zoomgov.com/rec/play/..._ (same as above; X may be empty)

## Building from sources
If you wish to build from sources, here is a quick howto. First, you need to clone the repository and enter it with a terminal. Then:
### Linux
Run the command `./devscript.sh compile`. It basically installs all the dependencies with pip in a temporary directory, then zips it.

### Windows
* Install [pyinstaller](https://www.pyinstaller.org/) (usually `pip install -U pyinstaller`) 
* Run the command `wincompile.bat`. It calls just calls `pyinstaller` and cleans the generated folders and files, leaving only the exe file. 

## Requirements
All dependencies are bundled within the executable. This allows to make a standalone execution without need for external libraries.

If you wish to build it yourself, see `requirements.txt`. The most important requirement is [requests](https://github.com/psf/requests). Please see [acknowledgements](#acknowledgements) for a note on that.

## Acknowledgements
The folder executable contains [requests](https://github.com/psf/requests) (and its dependencies), an awesome wrapper for HTTP(s) calls. Please check them out!
