# PodBlast

PodBlast is a simple podcast feed tracker written in Python using a GTK/Glade
front-end interface. It was designed to be lightweight and simple, allowing
users to subscribe and listen to their favorite feeds.

## Dependencies

PodBlast was developed on Gentoo and requires the following system packages:

 * **Python v.3** (python-3.4) - Everybody's favorite scripting language
 * **GTK+ v.3** (gtk+-3.12.2) - The Gnome Toolkit (a GUI library)
 * **GStreamer v.1** (gstreamer-1.2.4-r2) - A robust media handling library
 * **PyGObject v.3** (pygobject-3.12.2) - GTK+ bindings for Python
 * **GStreamer v.1** (gst-python-1.2.1) - Gstreamer bindings for Python

PodBlast requires the following python libraries:

 * **GObject** (gi) to fetch 'Gst' and 'Gtk' libraries in Python 3,
 * **System** (sys) to close the program,
 * **Regex** (re) to parse and verify URLs,
 * **Time** (time) to prase and convert time and zone information,
 * **FeedParser** (feedparser) to fetch and parse remote RSS feeds, and
 * **JSON** (json) to save and load user data.

# Using PodBlast

## GTK+ Frontend

PodBlast was primarily developed using Gentoo GNU/Linux for use on an up-to-date
linux platform. So long as its dependencies are met, it can be started using the
bash script in the root directory of the program:

```
#!bash
$ ./podblast
```

Because PodBlast is still in an early development state, its terminal output is
quite verbose. It is reccomended to run the program with an open terminal so you
can see what is happening on the back-end in case anything goes wrong.

## Python Shell (Backend)

The easiest way to run the PodBlast back-end is to instantiate an object in a
Python 3 shell started from the ```/src/``` directory, and manipulate the
streamer via command line:

```
#!python
>>> from podblast import PodBlast
>>> feed_url = http://feeds.feedburner.com/mbmbam
>>> blaster = PodBlast()                              # Instantiate PodBlast
>>> blaster.register_feed(feed_url)                   # Fetch the feed data
>>> blaster.set(0, 0)                                 # Feed and episode PKIDs
>>> blaster.play_pause()                              # Begin playback
>>> blaster.stop()                                    # Stop playback
```
