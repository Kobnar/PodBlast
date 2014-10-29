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

import podblast
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)    # Unix signal handler for Gtk.main() interrupt...

#------------------------------------------------------------------------------#

podblast_version = 'v.0.2.1'

if __name__ == '__main__':
    blaster = podblast.PodBlast()
    blaster.ux.main_window.set_title('PodBlast (' + podblast_version + ')')
    blaster.main()