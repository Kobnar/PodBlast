#------------------------------------------------------------------------------#
#
#     Copyright 2014 by Konrad R.K. Ludwig.
#
#     This file is part of PodBlast.
#
#     PodBlast is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#     PodBlast is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#   along with PodBlast. If not, see <http://www.gnu.org/licenses/>.
#
#------------------------------------------------------------------------------#

import database
import stream
import gtkhandler

#------------------------------------------------------------------------------#

class PodBlast (database.Database):
    """
    The primary PodBlast class with all of the necessary implementatons to fetch
    data from a remote feed, save/load data using JSON, and set/control a
    streaming audio channel.
    """
    def __init__(self):
        print ('Initializing PodBlast...')
        # Defines state trackers:
        self.actv_feed_pkid = None
        self.actv_epsd_pkid = None

        # Calls parent class constructor:
        database.Database.__init__(self)

        # Instantiates 'Stream' component object:
        self.stream = stream.Stream()

    #---------------- ----- --- --- - - - -  -     -
    # Stream controls:

    # Sets the PKID values of the "state tracker" (ie: 'self.actv_feed_pkid' and
    # 'self.actv_epsd_pkid') values:
    def set (self, feed_pkid, epsd_pkid):
        max_feed_pkid = len(self.feeds)
        if feed_pkid != None:
            if feed_pkid >= max_feed_pkid or feed_pkid < 0:
                print ('PodBlast:\tFeed index out of range.')
            else:
                max_epsd_pkid = len(self.feeds[feed_pkid].episodes)
                if (epsd_pkid != None
                    and (epsd_pkid >= max_epsd_pkid
                        or epsd_pkid < 0)):
                    print ('PodBlast:\tEpisode index out of range.')
                else:
                    print ('PodBlast:\tSetting new PKID pair: [', feed_pkid, ', ', epsd_pkid, ']')
                    self.actv_feed_pkid = feed_pkid
                    self.actv_epsd_pkid = epsd_pkid
                    if (epsd_pkid != None
                        and self.check_new(
                            feed_pkid,
                            epsd_pkid)):
                        self.mark_old(feed_pkid, epsd_pkid)
                    self.reset()
        else:
            self.actv_feed_pkid = None
            self.actv_epsd_pkid = None

    # Stops the current stream, gets the desired URL based on the "state
    # tracker" and passes that url to the player:
    def reset(self):
        self.stream.stop()
        if (self.actv_feed_pkid != None
            and self.actv_epsd_pkid != None):
            feed = self.feeds[self.actv_feed_pkid]
            episode = feed.episodes[self.actv_epsd_pkid]
            media_url = episode.media[0]
            self.stream.set(media_url)

    # Pauses or plays GStreamer playback based on the current player state:
    def play_pause (self):
        if self.stream.player_state is not 'PLAYING':
            self.stream.play()
        else:
            self.stream.pause()

    # Stops GStreamer playback and sets the episode tracker to "None":
    def stop (self):
        self.stream.stop()
        self.set(self.actv_feed_pkid, None)

    # Starts playing the "next" episode in the feed:
    def next (self):
        max_pkid = len(self.feeds[self.actv_feed_pkid].episodes)
        if self.actv_epsd_pkid < max_pkid:
            self.actv_epsd_pkid += 1
            self.reset()
            self.play_pause()
        else:
            print ("PodBlast:\tAlready at the end of the current playlist.")

    # Starts playing the "previous" episode in the feed:
    def prev (self):
        if self.actv_epsd_pkid > 0:
            self.actv_epsd_pkid -= 1
            self.reset()
            self.play_pause()
        else:
            print ("PodBlast:\tAlready at the beginning of the current playlist.")

    # Skips forward:
    def ffwd (self):
        self.stream.ffwd()

    # Skips backward:
    def rwnd (self):
        self.stream.rwnd()

    # Nullifies the stream (for thread-safe quitting):
    def null (self):
        self.set(None, None)
        self.stream.null()

    # CLI interface to print feeds:
    def get_feeds (self):
        for index, feed in enumerate(feeds):
            print (index + ": " + feed.title)

    # CLI interface to print episodes
    def get_episodes (self, actv_feed_pkid):
        for index, epsd in enumerate(self.feeds[actv_feed_pkid].episodes):
            print (index + ": " + epsd.title)

    # Returns the player state (eg: 'PLAYING'):
    def get_player_state (self):
        return self.stream.player_state

    # Gets the current stream position (in seconds):
    def get_position (self):
        return self.stream.get_position()

    # Sets the current stream position (in seconds):
    def set_position (self, raw_seconds):
        self.stream.set_position(raw_seconds)