#!/usr/bin/python

# A simple application indicator to change display backlight brightness.
# It sets a GConf setting on which gnome-power-manager reacts.
#
# Note that it only works for displays with configurable backlight,
# and only when the computer does not run on battery.

# MIT LICENSE
# Copyright (c) 2011 Markus Pointner <markus.pointner (at) mooware.at>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from os.path import dirname

import pygtk
pygtk.require('2.0')

import gtk
import gconf
import appindicator

# GConf key for the brightness setting. takes a value from 0 - 100.
BRIGHTNESS_KEY = "/apps/gnome-power-manager/backlight/brightness_ac"

class BrightnessIndicator:
  def __init__(self):
    # create a menu
    self.menu = gtk.Menu()
    self.menu.connect("destroy", self.destroy_indicator)
    self.menu_items = []
    self.current_index = -1

    # create items for the menu
    prev_item = None
    for i in range(0, 11):
      item = gtk.RadioMenuItem(prev_item, str(i))
      prev_item = item
      item.connect("activate", self.item_activate)
      item.show()
      self.menu.append(item)
      self.menu_items.append(item)

    # prepare gconf
    self.gconf = gconf.client_get_default()
    self.gconf.add_dir(dirname(BRIGHTNESS_KEY), gconf.CLIENT_PRELOAD_NONE)
    self.gconf_notify_id = self.gconf.notify_add(BRIGHTNESS_KEY,
                                                 self.gconf_value_changed)
    self.gconf_value_changed(self.gconf)

    # create the indicator. i hope that the "gnome-brightness-applet" icon is
    # distributed with gnome by default.
    self.indicator = appindicator.Indicator("backlight-indicator",
                                            "gnome-brightness-applet",
                                            appindicator.CATEGORY_HARDWARE)
    self.indicator.set_status(appindicator.STATUS_ACTIVE)

    # show the menu
    self.menu.show()
    self.indicator.set_menu(self.menu)

  def item_activate(self, item):
    new_index = int(item.get_label())
    if new_index != self.current_index:
      self.current_index = new_index
      self.gconf.set_int(BRIGHTNESS_KEY, new_index * 10)

  def gconf_value_changed(self, client, *args, **kwargs):
    new_value = client.get_int(BRIGHTNESS_KEY)
    new_index = int(round(new_value / 10.0))
    if new_index != self.current_index:
      self.menu_items[new_index].set_active(True)

  def destroy_indicator(self):
    if self.gconf_notify_id != 0:
      self.gconf.notify_remove(self.gconf_notify_id)

if __name__ == "__main__":
  indicator = BrightnessIndicator()
  gtk.main()
