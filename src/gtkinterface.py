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

        print ('...Connecting to GTK/Glade interface file.')
        # Defines the GTK/Glade interface source file and 'Gtk.Builder' object.
        self.ux_source = 'ux/podblast.glade'
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(self.ux_source)

        print ('...Linking to GTK front-end objects.')
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
        self.episode_treeview.connect('size-allocate', self.episode_treeview_changed)
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
        # print ('rebuild_feed_list() called.')
        self.feed_list.clear()
        for feed_title in feed_titles:
            self.feed_list.append(feed_title)

    def rebuild_episode_list (self, episode_input):
        # print ('rebuild_episode_list() called.')
        self.episode_list.clear()
        for episode in episode_input:
            self.episode_list.append(episode)

    def refresh_episode_list (self, actv_epsd_pkid):
        # print ('refresh_episode_list() called.')
        for episode in self.episode_list:
            # Sets icon marking the currently playing episode:
            if episode[0] == actv_epsd_pkid:
                episode[1] = True
            else:
                episode[1] = False
 
            # Bolds unheard podcasts:
            if episode[3] == True:
                episode[4] = 700
            else:
                episode[4] = 400

    def mark_old (self):
        for episode in self.episode_list:
            if episode[0] == self.actv_epsd_pkid:
                episode[3] = False

    # Auto-scrolls the episode TreeView:
    def episode_treeview_changed ( self, widget, event, data=None ):
        adjustment = widget.get_vadjustment()
        adjustment.set_value( adjustment.get_upper() - adjustment.get_page_size() )

    def get_feed_pkid (self):
        # print ('get_feed_pkid() called.')
        # feed_iter = self.feed_treeview.get_selection().get_selected()[1]
        feed_iter = self.feed_combo.get_active_iter()
        if feed_iter:
            return self.feed_list[feed_iter][0]

    def get_epsd_pkid (self):
        # print ('get_epsd_pkid() called.')
        episode_iter = self.episode_treeview.get_selection().get_selected()[1]
        # print ('Episode iter: ' + str(self.episode_list[episode_iter][0]))
        return self.episode_list[episode_iter][0]

    #---------------- ----- --- --- - - - -  -     -
    # Surrogate player controls:

    def stop (self):
        self.actv_epsd_pkid = None
        self.refresh_episode_list(self.actv_epsd_pkid)

    def next (self):
        self.actv_epsd_pkid += 1
        self.mark_old()
        self.refresh_episode_list(self.actv_epsd_pkid)

    def prev (self):
        self.actv_epsd_pkid -= 1
        self.mark_old()
        self.refresh_episode_list(self.actv_epsd_pkid)

    #---------------- ----- --- --- - - - -  -     -
    # Setting th player GTK+ button "sensitivity" states:

    def set_player_buttons (self, state):
        if state == 'NULL':
            # print ('set_player_buttons_null() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.prev_button.set_sensitive(False)
            # self.rwnd_button.set_sensitive(False)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
            # self.ffwd_button.set_sensitive(False)
            self.next_button.set_sensitive(False)
        elif state == 'READY':
            # print ('set_player_buttons_ready() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.prev_button.set_sensitive(False)
            # self.rwnd_button.set_sensitive(False)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
            # self.ffwd_button.set_sensitive(False)
            self.next_button.set_sensitive(False)
        elif state == 'PLAY':
            # print ('set_player_buttons_playing() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PAUSE, 4)
            self.prev_button.set_sensitive(True)
            # self.rwnd_button.set_sensitive(True)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(True)
            # self.ffwd_button.set_sensitive(True)
            self.next_button.set_sensitive(True)
        elif state == 'PAUSED':
            # print ('set_player_buttons_paused() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.prev_button.set_sensitive(True)
            # self.rwnd_button.set_sensitive(True)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(True)
            # self.ffwd_button.set_sensitive(True)
            self.next_button.set_sensitive(True)
        else:
            # print ('set_player_buttons_dead() called.')
            self.play_image.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.prev_button.set_sensitive(False)
            # self.rwnd_button.set_sensitive(False)
            self.play_button.set_sensitive(False)
            self.stop_button.set_sensitive(False)
            # self.ffwd_button.set_sensitive(False)
            self.next_button.set_sensitive(False)

    #---------------- ----- --- --- - - - -  -     -
    # Dialog windows:

    def error_dialog (self, message):
        message_dialog = Gtk.MessageDialog(
            None, 
            Gtk.DialogFlags.MODAL, 
            Gtk.MessageType.ERROR, 
            Gtk.ButtonsType.OK, 
            message)
        message_dialog.set_title('Error!')
        message_dialog.run()
        message_dialog.destroy()

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

    def get_add_feed_url (self):
        return self.add_feed_entry.get_text()

    # Clears and hides the "Add Feed" dialogue:
    def add_feed_hide (self):
        self.add_feed_dialog.hide()
        self.add_feed_entry.set_text('')

    #---------------- ----- --- --- - - - -  -     -
    # Save/Load dialogues:

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