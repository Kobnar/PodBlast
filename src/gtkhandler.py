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

import gtkinterface

#------------------------------------------------------------------------------#
# NOTE:
#     This class handles the signals sent to the PodBlast back-end by its
#   GTK/Glade front-end. It is not designed to invoke or require any GTK/Glade
#   libraries. All members/methods requiring GTK/Glade libraries to work are
#   defined in 'src/gtkinterface.py' and accessed using the user interface
#   component 'ux'.
#------------------------------------------------------------------------------#

class GTKHandler(object):

    def __init__(self):
        print ('Initializing GTK signal handler...')

        # Instantiates and connects GTK/Glade user interface component:
        print ('...Creating user interface coponent.')
        self.ux = gtkinterface.GTKInterface()

        print ('...Connecting front-end signals to back-end methods.')
        # Player controls:
        self.ux.gtk_builder.connect_signals(self)

    def gtk_main (self):
        print ('GTK Handler "main" function called.')
        self.rebuild_feed_list()
        self.refresh_player_buttons()
        self.ux.main()

    # Front-end signal handlers:

    def on_main_window_delete_event (self, widget, *args):
        self.stream.null()
        self.save()
        self.ux.main_quit()

    def on_load_menuitem_activate (self, *args):
        self.load()

    def on_save_menuitem_activate (self, *args):
        self.save()

    def on_feed_combo_changed (self, feed_combo):
        # Gets 'feed_pkid' from user interface:
        feed_iter = feed_combo.get_active_iter()
        feed_model = feed_combo.get_model()
        feed_pkid = feed_model[feed_iter][0]

        # Updates state tracker:
        self.feed_pkid = feed_pkid
        self.episode_pkid = None

        # Refreshes episode treeview:
        self.rebuild_episode_list()

    def on_episode_treeview_cursor_changed (self, *args):
        # Assume a change means something is selected, which will pass cleanly
        # to 'self.play()':
        self.ux.set_player_buttons_ready()

    def on_episode_treeview_row_activated (self, *args):
        # Get the pkid for the row and update the GUI, states and player:
        self.episode_pkid = self.ux.get_episode_pkid()
        self.reset()
        self.play_pause()
        self.refresh_player_buttons()
        self.ux.refresh_episode_list(self.episode_pkid)

    def on_play_button_clicked (self, button):
        print ('"Play" button pressed.')
        if self.episode_pkid != None:
            self.play_pause()
            self.refresh_player_buttons()
        else:
            self.episode_pkid = self.ux.get_episode_pkid()
            self.reset()
            self.play_pause()
            self.refresh_player_buttons()
            self.ux.refresh_episode_list(self.episode_pkid)

    def on_stop_button_clicked (self, button):
        print ('"Stop" button pressed.')
        self.stop()
        self.refresh_player_buttons()
        self.ux.refresh_episode_list(self.episode_pkid)

    def on_next_button_clicked (self, button):
        print ('"Next" button pressed.')
        self.next()
        self.refresh_player_buttons()
        self.ux.refresh_episode_list(self.episode_pkid)

    def on_prev_button_clicked (self, button):
        print ('"Previous" button pressed.')
        self.prev()
        self.refresh_player_buttons()
        self.ux.refresh_episode_list(self.episode_pkid)

    def on_rwnd_button_clicked (self, button):
        print ('Rewind feature not implemented yet.')

    def on_ffwd_button_clicked (self, button):
        print ('Rewind feature not implemented yet.')

    # Data management methods:

    def rebuild_feed_list (self):
        # TODO: Need test to pass subscribed feeds only.
        feed_titles = []
        for index, feed in enumerate(self.feeds):
            feed_titles.append([index, feed.title])
        self.ux.rebuild_feed_list(feed_titles)

    def rebuild_episode_list (self):
        episode_input = []
        for index, episode in enumerate(self.feeds[self.feed_pkid].episodes):
            self.ux.refresh_episode_list(index)
            episode_input.append([index, episode.title, 400])
        self.ux.rebuild_episode_list(episode_input)

    # User interface updates:

    def refresh_player_buttons (self):
        state = self.stream.player_state
        if self.feed_pkid == None:
            self.ux.set_player_buttons_dead()
        elif self.episode_pkid != None:
            if state == 'NULL':
                self.ux.set_player_buttons_null()
            elif state == 'READY':
                self.ux.set_player_buttons_ready()
            elif state == 'PAUSED':
                self.ux.set_player_buttons_paused()
            elif state == 'PLAYING':
                self.ux.set_player_buttons_playing()
        elif self.episode_cursor_pkid != None:
            self.ux.set_player_buttons_ready()