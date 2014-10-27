#------------------------------------------------------------------------------#\
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

class GTKHandler:
    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Window Handling:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def onDeleteMainWindow(self, *args):
        # Stop, save and quit:
        self.save_feeds()
        self.end_program(*args)

    def end_program (self, *args):
        gtk.main_quit(*args)

    def onDeleteAddFeedDiag(self, *args):
        self.close_add_feed_diag()
        return True

    def close_add_feed_diag(self):
        # Close dialogue and empty fields:
        self.add_feed_diag.hide()
        self.ap_url_entry.set_text("")

    def onDeleteErrDiag(self, *args):
        self.err_diag.hide()
        self.err_diag_label.set_text("")
        return True

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Player Controls:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def onPlayPress(self, button):
        self.stream.play_pause()

    def onStopPress(self, button):
        self.stream.stop()

    def onPrevPress(self, button):
      state.player.prev()

    def onNextPress(self, button):
      state.player.next()

    # def onRwndPress(self, button):
    #   state.player.rwnd()

    # def onFfwdPress(self, button):
    #   state.player.ffwd()

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Feed Subscription Management:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def onAddFeed(self, button):
        self.add_feed_diag.show()

    def onAddFeedCancel(self, button):
        self.close_add_feed_diag()

    def onAddFeedAdd(self, button):
        subscribed = self.subscribe_feed()
        if subscribed == True:
            self.close_add_feed_diag()

    def onDeleteFeed(self, button):
        self.unsubscribe_feed()

    def onFeedActivate(self, treeview, iter, tvc):
        self.pb.feed_manager.activate()

    def onFeedRightClick(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor( path, col, 0)
                self.feed_menu_split.set_visible(True)
                self.feed_menu_edit.set_visible(True)
                self.feed_menu_del.set_visible(True)
                self.feed_menu.popup( None, None, None, event.button, time)
            else:
                self.feed_menu_split.set_visible(False)
                self.feed_menu_edit.set_visible(False)
                self.feed_menu_del.set_visible(False)
                self.feed_menu.popup( None, None, None, event.button, time)
            return True

    def onFeedRefresh (self, button):
        print ("Feed refresh not yet implimented.")

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Episode Management:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def onEpisodeActivate (self, treeview, iter, tvc):
        self.pb.episode_manager.activate()

    def onEpisodeRefreshClicked (self, button):
        print ("Episode refresh not yet implimented.")