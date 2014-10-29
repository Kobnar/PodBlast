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

import sys
try:
    from gi.repository import Gtk
except:
    print ("Error: Failed to load GTK+ bindings for Python.")
    sys.exit(1)

#------------------------------------------------------------------------------#

class GTKInterface(object):
    """
    An implementation to link the GTK/Glade user interface objects to the
    PodBlast back-end along with certain methods to get and set user interface
    data.
    """
    def __init__(self):
        print ('Initializing GTK/Glade interface...')

        print ('...Connecting to GTK/Glade interface file.')
        # Defines the GTK/Glade interface source file and 'Gtk.Builder' object.
        self.ux_source = 'ux/podblast.glade'
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(self.ux_source)

        print ('...Linking to GTK front-end objects.')
        # Links to main window and dialog window objects:
        self.main_window = self.gtk_builder.get_object('main_window')

        # Links to 'TreeView' and 'ListStore' objects...
        self.feed_treeview = self.gtk_builder.get_object('feed_treeview')
        self.feed_list = self.gtk_builder.get_object('feed_list')
        self.episode_treeview = self.gtk_builder.get_object('episode_treeview')
        self.episode_list = self.gtk_builder.get_object('episode_list')

        # Links to player buttons:
        self.prev_button = self.gtk_builder.get_object('prev_button')
        # self.rwnd_button = self.gtk_builder.get_object('rwnd_button')
        self.play_button = self.gtk_builder.get_object('play_button')
        self.play_image = self.gtk_builder.get_object('play_image')
        self.stop_button = self.gtk_builder.get_object('stop_button')
        # self.ffwd_button = self.gtk_builder.get_object('ffwd_button')
        self.next_button = self.gtk_builder.get_object('next_button')

    # Draws all the windows and starts the GTK+ loop:
    def main (self):
        self.main_window.show_all()
        Gtk.main()

    # Stops the GTK+ loop:
    def main_quit (self):
        Gtk.main_quit()

    #---------------- ----- --- --- - - - -  -     -
    # Refreshing and managing 'TreeView' data:

    def rebuild_feed_list (self, feed_titles):
        self.feed_list.clear()
        for feed_title in feed_titles:
            self.feed_list.append(feed_title)

    def rebuild_episode_list (self, episode_input):
        self.episode_list.clear()
        for episode in episode_input:
            self.episode_list.append(episode)

    def refresh_episode_list (self, active_episode_pkid = None):
        for episode in self.episode_list:
            if episode[0] == active_episode_pkid:
                episode[2] = 700
            else:
                episode[2] = 400

    def get_feed_pkid (self):
        feed_iter = self.feed_treeview.get_selection().get_selected()[1]
        return self.feed_list[feed_iter][0]

    def get_episode_pkid (self):
        episode_iter = self.episode_treeview.get_selection().get_selected()[1]
        return self.episode_list[episode_iter][0]

    #---------------- ----- --- --- - - - -  -     -
    # Setting th player GTK+ button "sensitivity" states:

    def set_player_buttons_dead (self):
        self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
        self.prev_button.set_sensitive(False)
        # self.rwnd_button.set_sensitive(False)
        self.play_button.set_sensitive(False)
        self.stop_button.set_sensitive(False)
        # self.ffwd_button.set_sensitive(False)
        self.next_button.set_sensitive(False)

    def set_player_buttons_null (self):
        self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
        self.prev_button.set_sensitive(False)
        # self.rwnd_button.set_sensitive(False)
        self.play_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        # self.ffwd_button.set_sensitive(False)
        self.next_button.set_sensitive(False)

    def set_player_buttons_ready (self):
        self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
        self.prev_button.set_sensitive(False)
        # self.rwnd_button.set_sensitive(False)
        self.play_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        # self.ffwd_button.set_sensitive(False)
        self.next_button.set_sensitive(False)

    def set_player_buttons_paused (self):
        self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
        self.prev_button.set_sensitive(True)
        # self.rwnd_button.set_sensitive(True)
        self.play_button.set_sensitive(True)
        self.stop_button.set_sensitive(True)
        # self.ffwd_button.set_sensitive(True)
        self.next_button.set_sensitive(True)

    def set_player_buttons_playing (self):
        self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PAUSE, 4)
        self.prev_button.set_sensitive(True)
        # self.rwnd_button.set_sensitive(True)
        self.play_button.set_sensitive(True)
        self.stop_button.set_sensitive(True)
        # self.ffwd_button.set_sensitive(True)
        self.next_button.set_sensitive(True)
