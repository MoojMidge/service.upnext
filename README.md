[![GitHub release](https://img.shields.io/github/release/MoojMidge/service.upnext.svg)](https://github.com/MoojMidge/service.upnext/releases)
[![CI](https://github.com/MoojMidge/service.upnext/workflows/CI/badge.svg)](https://github.com/MoojMidge/service.upnext/actions?query=workflow:CI)
[![Codecov status](https://img.shields.io/codecov/c/github/MoojMidge/service.upnext/master)](https://codecov.io/gh/MoojMidge/service.upnext/branch/master)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv2-yellow.svg)](https://opensource.org/licenses/GPL-2.0)
[![Contributors](https://img.shields.io/github/contributors/MoojMidge/service.upnext.svg)](https://github.com/MoojMidge/service.upnext/graphs/contributors)

Personal fork of service.upnext (commits are often untested and cause addon to break) that implements:
- Automatic end credits detection
- Provides UpNext video listings for use as "UpNext ..." episode and movie widgets
- Provides "More like this..." and "Watched Movie/TVShow recommendations" video listings for use as widgets
- Shuffle (random, non-sequential) playback mode (requires skin integration, or use of internal skin)
- Added support for movie sets
- Multi-threaded event driven code
- More skin/popup setting (position, colour)
- More addon settings (mark as watched, play/resume next, queuing)
- More developer options (improved logging, integrated simulation mode for testing)
- Improved compatibility with playlists, plugins, and other non-library media
- Experimental use of TheMovieDb Helper players for automatic integration with any plugin that has a player
- Built-in methods to simplify plugin integration

Changelog: [changelog.txt](changelog.txt)

Official release available through official Kodi addon repository and at [https://github.com/im85288/service.upnext/](https://github.com/im85288/service.upnext/)
<br />
<br />
# Up Next - Proposes to play the next episode automatically

This Kodi add-on shows a Netflix-style notification for watching the next episode. After a few automatic iterations it asks the user if he is still there watching.

A lot of existing add-ons already integrate with this service out-of-the-box.

## Settings
The add-on has various settings to fine-tune the experience, however the default settings should be fine for most.

  * Simple or fancy mode (defaults to fancy mode, but a more simple interface is possible)
  * The notification time can be adjusted (defaults to 30 seconds before the end)
  * The default action can be configured, i.e. should it advance to the next episode (default) when the user does not respond, or stop
  * The number of episodes to play automatically before asking the user if he is still there (defaults to 3 episodes)

> NOTE: The add-on settings are found in the Kodi add-ons section, in the *Services* category.

For [Addon Integration](https://github.com/im85288/service.upnext/wiki/Addon-Integration) and [Skinners](https://github.com/im85288/service.upnext/wiki/Skinners) see the [wiki](https://github.com/im85288/service.upnext/wiki)
