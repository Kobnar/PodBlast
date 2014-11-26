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

import sys
from pbutils import format_time
try:
    from gi.repository import Gtk
except:
    print ("Error: Failed to load GTK+ bindings for Python.")
    sys.exit(1)

#------------------------------------------------------------------------------#

class GTKInterface(object):
    """
    An implementation to link the GTK/Glade user interface objects to python and
    provide a collection of methods to handle state changes.
    """
    def __init__(self):
        print ('Initializing GTK/Glade interface...')
        # Creates state trackers for user interface:
        self.actv_feed_pkid = None
        self.actv_epsd_pkid = None
        self.player_state = 'NULL'

        # Defines the GTK/Glade interface source file and 'Gtk.Builder' object.
        self.ux_source = 'ux/podblast.glade'
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(self.ux_source)

        # Links to main window and dialog window objects:
        self.main_window = self.gtk_builder.get_object('main_window')
        self.about_dialog = self.gtk_builder.get_object('about_dialog')
        self.add_feed_dialog = self.gtk_builder.get_object('add_feed_dialog')

        # Links to "Add Feed" dialogue entry box:
        self.add_feed_entry = self.gtk_builder.get_object('add_feed_entry')

        # Links to 'TreeView' and 'ListStore' objects...
        self.feed_combo = self.gtk_builder.get_object('feed_combo')
        # self.feed_treeview = self.gtk_builder.get_object('feed_treeview')
        self.feed_list = self.gtk_builder.get_object('feed_list')
        self.episode_treeview = self.gtk_builder.get_object('episode_treeview')
        self.episode_list = self.gtk_builder.get_object('episode_list')

        # Links to player buttons:
        self.prev_button = self.gtk_builder.get_object('prev_button')
        self.rwnd_button = self.gtk_builder.get_object('rwnd_button')
        self.play_button = self.gtk_builder.get_object('play_button')
        self.play_image = self.gtk_builder.get_object('play_image')
        self.stop_button = self.gtk_builder.get_object('stop_button')
        self.ffwd_button = self.gtk_builder.get_object('ffwd_button')
        self.next_button = self.gtk_builder.get_object('next_button')

        # Links to player time slider:
        self.time_position_label = self.gtk_builder.get_object('time_position_label')
        self.time_duration_label = self.gtk_builder.get_object('time_duration_label')
        self.time_scale = self.gtk_builder.get_object('time_scale')
        self.time_scale_adjustment = self.gtk_builder.get_object('time_scale_adjustment')

    # Draws all the windows and starts the GTK+ loop:
    def main (self):
        self.refresh_player_buttons()
        self.main_window.show_all()
        Gtk.main()

    # Stops the GTK+ loop:
    def main_quit (self):
        Gtk.main_quit()

    #---------------- ----- --- --- - - - -  -     -
    # Refreshing and managing 'TreeView' data:

    def refresh_ux (self):
        self.refresh_episode_list()
        self.refresh_player_buttons()

    # Replaces the feed list with a new list:
    def rebuild_feed_list (self, feed_titles):
        # print ('rebuild_feed_list() called.')
        self.feed_list.clear()
        for feed_title in feed_titles:
            self.feed_list.append(feed_title)

    # Replaces the episode list with a new list:
    def rebuild_episode_list (self, episode_input):
        # print ('rebuild_episode_list() called.')
        self.episode_list.clear()
        for episode in episode_input:
            self.episode_list.append(episode)
        self.refresh_episode_list()
        # adjustment = self.episode_treeview.get_vadjustment()
        self.episode_treeview.scroll_to_cell(len(self.episode_list) - 1)

    # Updates the front-end data to reflect the player state.
    def refresh_episode_list (self):
        print ('GTKInterface:\trefresh_episode_list() called.')
        for episode in self.episode_list:
            # Sets icon marking the currently playing episode:
            if episode[0] == self.actv_epsd_pkid:
                episode[1] = True
                if self.player_state == 'PLAYING':
                    episode[5] = 'media-playback-start'
                else:
                    episode[5] = 'media-playback-pause'
            else:
                episode[1] = False

            # Bolds unheard podcasts:
            if episode[3] == True:
                episode[4] = 700
            else:
                episode[4] = 400

    # Un-bolds podcasts which have been played.
    def mark_old (self):
        # print ('GTKInterface:\tmark_old() called.')
        for episode in self.episode_list:
            if episode[0] == self.actv_epsd_pkid:
                print ('GTKInterface:\tMarking episode #'
                    + str(self.actv_epsd_pkid) + ' as "old".')
                episode[3] = False

    # Fetches the PKID of the currently selected feed.
    def get_feed_pkid (self):
        # print ('get_feed_pkid() called.')
        # feed_iter = self.feed_treeview.get_selection().get_selected()[1]
        feed_iter = self.feed_combo.get_active_iter()
        if feed_iter:
            return self.feed_list[feed_iter][0]

    # Fetches the PKID of the currently selected episode.
    def get_epsd_pkid (self):
        # print ('get_epsd_pkid() called.')
        episode_iter = self.episode_treeview.get_selection().get_selected()[1]
        # print ('Episode iter: ' + str(self.episode_list[episode_iter][0]))
        return self.episode_list[episode_iter][0]

    #---------------- ----- --- --- - - - -  -     -
    # Surrogate player controls (update's ux state):

    def play_pause (self):
        if self.player_state is not 'PLAYING':
            self.play()
        else:
            self.pause()

    def play (self):
        self.mark_old()
        self.refresh_ux()

    def pause (self):
        self.refresh_ux()

    def stop (self):
        self.refresh_ux()

    def null (self):
        self.refresh_ux()

    #---------------- ----- --- --- - - - -  -     -
    # Refreshing/setting the time slider and labels:

    def set_time_scale (self, position_data):
        duration, position = position_data
        self.set_time_scale_duration(duration)
        self.set_time_scale_position(position)

    def set_time_scale_duration (self, duration):
        duration = int(round(duration, 0))
        duration_string = format_time(duration).strftime('%H:%M:%S')
        self.time_scale_adjustment.set_upper(duration)
        self.time_duration_label.set_text(duration_string)

    def set_time_scale_position (self, position):
        position = int(round(position, 0))
        position_string = format_time(position).strftime('%H:%M:%S')
        self.time_scale_adjustment.set_value(position)
        self.time_position_label.set_text(position_string)

    def get_time_scale_position (self):
        return self.time_scale_adjustment.get_value()

    #---------------- ----- --- --- - - - -  -     -
    # Player GTK+ button "sensitivity" states:

    # Updates the icons for the player controls (eg: cannot "play" if nothing
    # is selected)
    def set_player_buttons (self, state = 'DEAD'):
        if state == 'NULL':
            # print ('set_player_buttons_null() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.prev_button.set_sensitive(False)
            self.rwnd_button.set_sensitive(False)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
            self.ffwd_button.set_sensitive(False)
            self.next_button.set_sensitive(False)
        elif state == 'READY':
            # print ('set_player_buttons_ready() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.prev_button.set_sensitive(False)
            self.rwnd_button.set_sensitive(False)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
            self.ffwd_button.set_sensitive(False)
            self.next_button.set_sensitive(False)
        elif state == 'PLAYING':
            # print ('set_player_buttons_playing() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PAUSE, 4)
            self.prev_button.set_sensitive(True)
            self.rwnd_button.set_sensitive(True)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(True)
            self.ffwd_button.set_sensitive(True)
            self.next_button.set_sensitive(True)
        elif state == 'PAUSED':
            # print ('set_player_buttons_paused() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.prev_button.set_sensitive(True)
            self.rwnd_button.set_sensitive(True)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(True)
            self.ffwd_button.set_sensitive(True)
            self.next_button.set_sensitive(True)
        else:   # 'DEAD'
            # print ('set_player_buttons_dead() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.prev_button.set_sensitive(False)
            self.rwnd_button.set_sensitive(False)
            self.play_button.set_sensitive(False)
            self.stop_button.set_sensitive(False)
            self.ffwd_button.set_sensitive(False)
            self.next_button.set_sensitive(False)

    # A logic stream dictating the ux vs. player states:
    def refresh_player_buttons (self):
        if self.actv_feed_pkid == None:
            self.set_player_buttons('DEAD')
        elif self.actv_epsd_pkid != None:
            self.set_player_buttons(self.player_state)
        else:
            self.set_player_buttons('NULL')

    #---------------- ----- --- --- - - - -  -     -
    # Dialog windows:

    # A GTK error dialogue with a customizable message:
    def error_dialog (self, message):
        message_dialog = Gtk.MessageDialog(
            None, 
            Gtk.DialogFlags.MODAL, 
            Gtk.MessageType.ERROR, 
            Gtk.ButtonsType.OK, 
            message)
        message_dialog.set_title('PodBlast Message')
        message_dialog.run()
        message_dialog.destroy()

    # A GTK confirmation dialogue with a custom title and message:
    def confirm_dialog (self, title, message):
        message_dialog = Gtk.MessageDialog(
            None, 
            Gtk.DialogFlags.MODAL, 
            Gtk.MessageType.QUESTION, 
            Gtk.ButtonsType.OK_CANCEL, 
            message)
        message_dialog.set_title(title)
        response = message_dialog.run()
        message_dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return True
        else:
            return False

    # Shows the "Add Feed" dialogue:
    def add_feed_show (self):
        self.add_feed_dialog.show()

    # Gets the current "Add Feed" URL text:
    def get_add_feed_url (self):
        return self.add_feed_entry.get_text()

    # Clears and hides the "Add Feed" dialogue:
    def add_feed_hide (self):
        self.add_feed_dialog.hide()
        self.add_feed_entry.set_text('')

    #---------------- ----- --- --- - - - -  -     -
    # Save/Load dialogues:

    # A file-chooser to load a specific file:
    def load_dialog (self):
        file_chooser = Gtk.FileChooserDialog(
            "Open Database",    # Title
            None,               # Parent
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            )
        file_chooser.set_current_folder('data/')
        response = file_chooser.run()
        if response == Gtk.ResponseType.OK:
            file_name = file_chooser.get_filename()
            file_chooser.destroy()
            return file_name
        else:
            file_chooser.destroy()
            return None

    # A file-chooser to save to a specific file:
    def save_dialog (self):
        file_chooser = Gtk.FileChooserDialog(
            "Open Database",    # Title
            None,               # Parent
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
            )
        file_chooser.set_current_folder('data/')
        response = file_chooser.run()
        if response == Gtk.ResponseType.OK:
            file_name = file_chooser.get_filename()
            file_chooser.destroy()
            return file_name
        else:
            file_chooser.destroy()
            return None