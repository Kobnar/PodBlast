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

import re
import time
import datetime

#------------------------------------------------------------------------------#
#     The following function "validates" a URL, returning a parsed and cleaned
#   url string if the provided URL was valid or 'None' if it was bogus.
#------------------------------------------------------------------------------#

def validate_url (feed_url):
    # This regex string was shamelessly pulled from Django:
    regex_url = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    feed_url = re.match(regex_url, feed_url)
    if feed_url == None:
        return feed_url
    else:
        return feed_url.group(0)

#------------------------------------------------------------------------------#
#     The following two functions translate Python's 9-Tupile time format into
#   or back from a dictionary object with 'JSON' can handle.
#------------------------------------------------------------------------------#

def pack_time(timeinfo):
    return {
        'tm_year' : timeinfo.tm_year,
        'tm_mon' : timeinfo.tm_mon,
        'tm_mday' : timeinfo.tm_mday,
        'tm_hour' : timeinfo.tm_hour,
        'tm_min' : timeinfo.tm_min,
        'tm_sec' : timeinfo.tm_sec,
        'tm_wday' : timeinfo.tm_wday,
        'tm_yday' : timeinfo.tm_yday,
        'tm_isdst' : timeinfo.tm_isdst
    }

def unpack_time(timeinfo):
    return time.struct_time([
        timeinfo['tm_year'],
        timeinfo['tm_mon'],
        timeinfo['tm_mday'],
        timeinfo['tm_hour'],
        timeinfo['tm_min'],
        timeinfo['tm_sec'],
        timeinfo['tm_wday'],
        timeinfo['tm_yday'],
        timeinfo['tm_isdst']
        ])

#------------------------------------------------------------------------------#
#     The following function converts time given in raw seconds to a formatted
#   time object.
#------------------------------------------------------------------------------#

def format_time (raw_seconds):
    seconds = int(raw_seconds % 60)
    hours = int(raw_seconds / 60 / 60)
    minutes = int(raw_seconds / 60 - hours * 60)
    hhmmss = datetime.time(hours, minutes, seconds, 0, tzinfo=None)
    return hhmmss