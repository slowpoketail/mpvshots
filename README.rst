mpvshots
========

mpvshots is an automatic screenshot uploader for `mpv`_. After a bit of
configuration, you'll be able to automatically upload all screenshots you take
in mpv to `Twitter`_.

Components
----------

There are two major components of mpvshots. First, there is the eponymous
command line tool, *mpvshots*, which is your primary interface to all
functionality. The second component is the daemon which does all the actual
work, which is named *mpvshotsd*. You do not have to manually control this
daemon, and should use *mpvshots* to manage it.

How does it work?
-----------------

To upload a screenshot to Twitter (or somewhere else, as different backends are
theoretically possible), several things need to happen.

First of all, obviously, does the screenshot need to be taken, and *mpvshotsd*
must be somehow notified of this action. To simplify things, we simply have
*mpvshots* iniate the screenshot via mpv's IPC, then hand the screenshot off to
*mpvshotsd* via another IPC call, which will queue it for upload. You can in
fact replace mpv's screenshot command by a call to mpvshots, which makes the
entire process transparent, you just keep taking screenshots as usual.

To work, *mpvshotsd* obviously needs to be able to access your Twitter account.
To do this, *mpvshots* does OAUTH and save the credentials for the daemon to
access. It will save them in *~/.mpvshots/*. This is also where mpvshots'
configuration file will eventually be found.


.. _mpv: http://mpv.io/
.. _Twitter: https://twitter.com
