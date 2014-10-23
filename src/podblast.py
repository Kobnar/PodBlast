#------------------------------------------------------------------------------#
#   Copyright 2014 by Konrad R.K. Ludwig.
#
#   This file is part of PodBlast.
#
#   PodBlast is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#   PodBlast is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
# along with PodBlast. If not, see <http://www.gnu.org/licenses/>.
#
#------------------------------------------------------------------------------#


#import sys
#import datetime
import feedparser
import csv
import pygst
pygst.require("0.10")
import gst

#------------------------------------------------------------------------------#
# A podcast episode:
#------------------------------------------------------------------------------#

class Episode(object):
    def __init__(self, episode_source):
        # Defines episode data:
        self.url = episode_source.link
        self.title = episode_source.title
        self.description = episode_source.description
        self.dtg_published = episode_source.published_parsed
        # Compiles a list of embeded media urls:
        self.media = []
        for media_source in episode_source.media_content:
            self.media.append(media_source['url'])
        # Defines episode metadata:
        self.downloaded = episode_source.downloaded

#------------------------------------------------------------------------------#
# A podcast (aka: feed):
#------------------------------------------------------------------------------#

class Feed(object):
    def __init__(self, feed_source):
        # Extracts feed data:
        self.url = feed_source.url
        self.title = feed_source.title
        self.description = feed_source.description
        # Compiles a list of episodes:
        self.episodes = []
        for episode_source in feed_source.entries:
            self.episodes.append(Episode(episode_source))
        # Extracts feed metadata:
        self.valid = feed_source.valid
        self.subscribed = feed_source.subscribed

#------------------------------------------------------------------------------#
# An implementation to save and load PodBlast data:
#------------------------------------------------------------------------------#

class Database(object):
    def __init__(self):
        self.feeds = []

    #--------------------------------------------------------------------------#
    #     The following three classes workaround Python's single constructor
    #   limitation by sharing a uniform "template" of data. The prefix "LD"
    #   indicates the data is loaded from a 'cvs' file, while the prefix "FH"
    #   indicates the data is fetched using 'feedparser'. Both classes can be
    #   passed to the 'Feed' constructor to populate the feed's data.
    #--------------------------------------------------------------------------#

    # Episode data which has been loaded from a single row in a CVS file:
    class LDEpisodeSource:
        def __init__(self, csv_row):
            # Loads episode data:
            self.link = csv_row[1]
            self.title = csv_row[2]
            self.description = csv_row[3]
            self.published_parsed = csv_row[4]
            self.media_content = []
            # Loads episode metadata:
            self.downloaded = csv_row[5]

    # Feed data which has been loaded from a single row in a CVS file:
    class LDFeedSource:
        def __init__(self, csv_row):
            # Loads feed data:
            self.url = csv_row[0]
            self.title = csv_row[1]
            self.description = csv_row[2]
            self.entries = []
            # Loads feed metadata:
            self.valid = csv_row[3]
            self.subscribed = csv_row[4]

    # Feed data which has been fetched and parsed from a remote url:
    class FHFeedSource:
        def __init__(self, feed_url):
            # Tries to parse the podcast feed, prints error if it fails:
            # try:
                source = feedparser.parse(feed_url)
                self.title = source.feed.title
                self.description = source.feed.description
                self.entries = source.entries
                for entry in self.entries:
                    entry.downloaded = False
                self.valid = True
                self.subscribed = True
            # except:
            #     print ("Failed to parse feed: " + feed_url)
            #     self.valid = False
            #     self.subscribed = False
            # Defines url regardless:
                self.url = feed_url

    #--------------------------------------------------------------------------#
    #     The following three methods load data from the program's various
    #   CVS files and reconstructs them into objects.
    #--------------------------------------------------------------------------#

    # Loads all of the media content urls of a given episode:
    def load_media(self, episode_url):
        with open('media.csv', 'rb') as csvfile:
            media_reader = csv.reader(csvfile) #Database.CSVReader(csvfile).reader
            media_content = []
            (media_content.append({ 'url': url }) for url in
                [media[1] for row in media_reader if row[0] is episode_url])
            return media_content

    # Loads all of the episodes of a given feed:
    def load_episodes(self, feed_url):
        with open('episodes.csv', 'rb') as csvfile:
            episode_reader = csv.reader(csvfile) #Database.CSVReader(csvfile).reader
            entries = []
            for row in episode_reader:
                print ("Loading: " + row[0] + " == " + feed_url)
                if row[0] == feed_url:
                    source = Database.LDEpisodeSource(row)
                    episode_url = row[1]
                    source.media_content = self.load_media(episode_url)
                    entries.append(
                        Episode(source)
                        )
            return entries

    # Loads all of the feeds which have been saved by the user:
    def load_feeds(self):
        with open('feeds.csv', 'rb') as csvfile:
            feed_reader = csv.reader(csvfile) #Database.CSVReader(csvfile).reader
            feeds = []
            for row in feed_reader:
                feed_url = row[0]
                source = Database.LDFeedSource(row)
                source.entries = self.load_episodes(feed_url)
                feeds.append(
                    Feed(source)
                    )
            return feeds

    #--------------------------------------------------------------------------#
    #     The following three methods save the program's current data
    #   structure into a series of CVS files which can be loaded the
    #   next time our program starts.
    #--------------------------------------------------------------------------#

    # Saves an episode's media urls to a CVS file:
    def save_media(self, episode):
        with open('media.csv', 'wb') as csvfile:
            filewriter = csv.writer(csvfile)
            for media_url in episode.media:
                filewriter.writerow([
                    episode.url,
                    media_url
                    ])

    # Saves all of a feed's valid episodes to a CVS file:
    def save_episodes(self, feed):
        with open('episodes.csv', 'wb') as csvfile:
            filewriter = csv.writer(csvfile)
            for episode in feed.episodes:
                filewriter.writerow([
                    feed.url,
                    episode.url,
                    episode.title,
                    episode.description,
                    episode.dtg_published,
                    episode.downloaded
                    ])
                self.save_media(episode)

    # Saves all registered and valid feeds to a CVS file:
    def save_feeds(self):
        if self.feeds:
            with open('feeds.csv', 'wb') as csvfile:
                filewriter = csv.writer(csvfile)
                for feed in self.feeds:
                    if feed.valid:
                        filewriter.writerow([
                            feed.url,
                            feed.title,
                            feed.description,
                            feed.valid,
                            feed.subscribed
                            ])
                        self.save_episodes(feed)
        else:
            print ("No feeds to save.")

    #--------------------------------------------------------------------------#
    #     The following methods handle feed "registration" (ie: fetching a new
    #   feed based on a given url) and "subscription" (ie: a feed which is
    #   visible to the user, synced on load, etc.). This distinction is used
    #   to reduce the frequency with which the (relatively) slow 'feedparser'
    #   library is called.
    #--------------------------------------------------------------------------#

    # If a feed with the given url is found, sets 'subscribed' to 'True',
    #   otherwise prints error to console.
    def subscribe_feed(self, feed_url):
        feed_search = [feed for feed in self.feeds if feed.url is feed_url]
        if feed_search:
            for feed in feed_search:
                feed.subscribed = True
        else:
            print ("Could not find a valid feed to set subscription: " + feed_url)

    # If a feed with the given url is found, sets 'subscribed' to 'False':
    def unsubscribe_feed(self, feed_url):
        feed_search = [feed for feed in self.feeds if feed.url is feed_url]
        if feed_search:
            for feed in feed_search:
                feed.subscribed = False
        else:
            print ("Could not find a valid feed to unset subcription: " + feed_url)

    # Fetches feed data if the given feed_url is not already registered.
    def register_feed(self, feed_url):
        feed_search = [feed for feed in self.feeds if feed.url is feed_url]
        if feed_search:
            print ("Feed already registered: " + feed_url)
        else:
            # try:
                source = Database.FHFeedSource(feed_url)
                self.feeds.append(
                    Feed(source)
                    )
            # except:
                # print ("Failed to register feed: " + feed_url)

    # Deletes any feed objects with a url matching the given 'feed_url':
    def delete_feed(self, feed_url):
        feed_search = [feed for feed in self.feeds if feed.url is feed_url]
        for feed in (feeds for feed in feed_search if feed_search):
            feed_index = self.feeds.index(feed)
            self.feeds.remove(feed_index)

#------------------------------------------------------------------------------#
# An implementation to play podcast episode media using GStreamer:
#------------------------------------------------------------------------------#

class Player(object):
    def __init__(self):
        # Instantiates the 'GStreamer' player "engine" and defines the current
        #   output sink as 'pulseaudio':
        self.engine = gst.element_factory_make("playbin", "player")
        self.engine.set_property(
            "audio-sink",
            gst.element_factory_make("pulsesink", "pulse"
                )
            )
        # Instantiates the 'GStreamer' "bus":
        bus = self.engine.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        bus.connect('message', self.gst_message_handler)
        # Defines our own state handler for 'GStreamer':
        self.player_state = "NULL"

    #--------------------------------------------------------------------------#
    #     The following two methods interface with the 'GStreamer' bus to
    #   update our own state handler.
    #--------------------------------------------------------------------------#

    def gst_message_handler(self, bus, message):
        if message.type == gst.MESSAGE_STATE_CHANGED:
            old, new, pending = message.parse_state_changed()
            self.refresh_player_state(new)

    def refresh_player_state (self, state_msg):
        if state_msg == gst.STATE_NULL:
            self.player_state = "NULL"
        elif state_msg == gst.STATE_READY:
            self.player_state = "READY"
        elif state_msg == gst.STATE_PAUSED:
            self.player_state = "PAUSED"
        elif state_msg == gst.STATE_PLAYING:
            self.player_state = "PLAYING"

    #--------------------------------------------------------------------------#
    #     The following five methods constitute the "player controls" which
    #   interface with 'GStreamer' to 'set' the current media url and 'play'
    #   'pause' or 'stop' the current stream.
    #--------------------------------------------------------------------------#

    # Sets the current channel url:
    def set (self, channel_url):
        self.engine.set_property('uri', channel_url)

    # Basic play/pause function based on 'player_state':
    def play_pause (self):
        if self.player_state is not "PLAYING":
            self.engine.set_state(gst.STATE_PLAYING)
        else:
            self.pause()

    # Begins streaming playback:
    def play (self):
        self.engine.set_state(gst.STATE_PLAYING)

    # Pauses current playback (in-place):
    def pause (self):
        self.engine.set_state(gst.STATE_PAUSED)

    # Stops current playback (reset):
    def stop (self):
        self.engine.set_state(gst.STATE_READY)

#------------------------------------------------------------------------------#
# The "core" 'Feed' subscription management class:
#------------------------------------------------------------------------------#

class PodBlast (Database, Player):
    def __init__(self):
        # try:
            self.feeds = self.load_feeds()
        # except:
        #     print ("Failed to load feeds.")