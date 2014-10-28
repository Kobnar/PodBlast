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

class PodBlast (database.Database, gtkhandler.GTKHandler):
    """
    The 'core' PodBlast class with all of the necessary implementatons to fetch
    data from a remote feed, save/load data from CSV files, set and control a
    streaming audio, and interface with the PodBlast GTK/Glade frontend.
    """
    def __init__(self):
        print ('Initializing PodBlast...')

        # Defines state trackers:
        self.feed_pkid = None
        self.episode_pkid = None

        # Calls parent class constructors:
        database.Database.__init__(self)
        gtkhandler.GTKHandler.__init__(self)

        # Instantiates 'Player' component object:
        self.stream = player.Player()

    def main (self):
        print ('PodBlast "main" function called.')
        self.gtk_main()

    #---------------- ----- --- --- - - - -  -     -
    # Player controls:

    def set (self, feed_pkid, episode_pkid):
        max_feed_pkid = len(self.feeds)
        if (feed_pkid != None
            and (feed_pkid >= max_feed_pkid or feed_pkid < 0)):
            print ("Feed index out of range.")
        else:
            max_episode_pkid = len(self.feeds[feed_pkid].episodes)
            if (episode_pkid != None
                and (episode_pkid >= max_episode_pkid
                    or episode_pkid < 0)):
                print ("Episode index out of range.")
            else:
                self.feed_pkid = feed_pkid
                self.episode_pkid = episode_pkid
                self.reset()

    def reset(self):
        self.stream.stop()
        if (self.feed_pkid != None
            and self.episode_pkid != None):
            feed = self.feeds[self.feed_pkid]
            episode = feed.episodes[self.episode_pkid]
            media_url = episode.media[0]
            self.stream.set(media_url)
        print (str([self.feed_pkid, self.episode_pkid]))

    def play_pause (self):
        self.stream.play_pause()

    def stop (self):
        self.set(self.feed_pkid, None)
        self.stream.stop()

    def next (self):
        max_pkid = len(self.feeds[self.feed_pkid].episodes)
        if self.episode_pkid < max_pkid:
            self.episode_pkid += 1
            self.reset()
            self.play_pause()
        else:
            print ("Already at the end of the current playlist.")

    def prev (self):
        if self.episode_pkid > 0:
            self.episode_pkid -= 1
            self.reset()
            self.play_pause()
        else:
            print ("Already at the beginning of the current playlist.")