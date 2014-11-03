#------------------------------------------------------------------------------#\
#
#     Copyright 2014 by Konrad R.K. Ludwig. All rights reserved.
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
import player
import gtkhandler

#------------------------------------------------------------------------------#

class PodBlast (database.Database):
    """
    The primary PodBlast class with all of the necessary implementatons to fetch
    data from a remote feed, save/load data using JSON, set and control a
    streaming audio, and interface with the PodBlast GTK/Glade frontend.
    """
    def __init__(self):
        print ('Initializing PodBlast...')
        # Defines state trackers:
        self.actv_feed_pkid = None
        self.actv_epsd_pkid = None

        # Calls parent class constructors:
        database.Database.__init__(self)

        # Instantiates 'Player' component object:
        self.stream = player.Player()

    #---------------- ----- --- --- - - - -  -     -
    # Player controls:

    # Sets the PKID values of the "state tracker" (ie: 'self.actv_feed_pkid' and
    # 'self.actv_epsd_pkid') values:
    def set (self, actv_feed_pkid, actv_epsd_pkid):
        max_actv_feed_pkid = len(self.feeds)
        if actv_feed_pkid != None:
            if actv_feed_pkid >= max_actv_feed_pkid or actv_feed_pkid < 0:
                print ("Feed index out of range.")
            else:
                max_actv_epsd_pkid = len(self.feeds[actv_feed_pkid].episodes)
                if (actv_epsd_pkid != None
                    and (actv_epsd_pkid >= max_actv_epsd_pkid
                        or actv_epsd_pkid < 0)):
                    print ("Episode index out of range.")
                else:
                    self.actv_feed_pkid = actv_feed_pkid
                    self.actv_epsd_pkid = actv_epsd_pkid
                    print ('Checking if new.')
                    if (actv_epsd_pkid != None
                        and self.check_new(
                            actv_feed_pkid,
                            actv_epsd_pkid)):
                        self.mark_old(actv_feed_pkid, actv_epsd_pkid)
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
            print ('Reset successfully called: [' + str(self.actv_feed_pkid) + ',' + str(self.actv_epsd_pkid) + ']')

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
            print ("Already at the end of the current playlist.")

    # Starts playing the "previous" episode in the feed:
    def prev (self):
        if self.actv_epsd_pkid > 0:
            self.actv_epsd_pkid -= 1
            self.reset()
            self.play_pause()
        else:
            print ("Already at the beginning of the current playlist.")

    # CLI interface to print feeds:
    def get_feeds (self):
        for index, feed in enumerate(feeds):
            print (index + ": " + feed.title)

    # CLI interface to print episodes
    def get_episodes (self, actv_feed_pkid):
        for index, epsd in enumerate(self.feeds[actv_feed_pkid].episodes):
            print (index + ": " + epsd.title)