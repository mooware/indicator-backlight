#!/usr/bin/python

# A simple application indicator to change display backlight brightness.
# It uses DBus to talk to the GNOME PowerManager.
#
# Note that it only works if there is a backlight-capable device present.
# Notebooks and netbooks usually have adjustable backlight in their displays,
# but standalone devices might not have it.
# Check "/sys/class/backlight/" for backlight support.

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

import pygtk
pygtk.require('2.0')

import gtk
import appindicator
import dbus
from dbus.mainloop.glib import DBusGMainLoop


# This class encapsulates the mechanism by which we talk to the backlight.
# Currently, it uses the DBus interface of the GNOME PowerManager.
class BacklightAdapter:
  def __init__(self):
    bus = dbus.SessionBus()
    proxy = bus.get_object("org.gnome.PowerManager",
                           "/org/gnome/PowerManager/Backlight")
    self.dbus_interface = dbus.Interface(proxy, dbus_interface="org.gnome.PowerManager.Backlight")
    self.dbus_interface.connect_to_signal("Brightnesanged", self.brightness_changed)

    self.callback = None

  def get_value(self):
    return int(self.dbus_interface.GetBrightness())

  def set_value(self, value):
    self.dbus_interface.SetBrightness(value)

  def set_callback(self, callback):
    self.callback = callback

  def brightness_changed(self, changed_value):
    if callback:
      callback(changed_value)


# This is the main class. It creates and manages the indicator.
class IndicatorBacklight:
  def __init__(self, backlight):
    # create a menu
    self.menu = gtk.Menu()
    self.menu.connect("destroy", self.destroy_indicator)

    # create items for the menu
    self.menu_items = []
    self.current_item = None

    radio_group = None
    for i in range(0, 11):
      brightness_value = i * 10
      item = gtk.RadioMenuItem(radio_group, str(brightness_value) + "%")

      if radio_group == None:
        radio_group = item

      item.connect("activate", self.item_activate, brightness_value)
      item.show()
      self.menu.append(item)
      self.menu_items.append(item)

    # init the backlight adapter
    self.backlight = backlight
    self.backlight.set_callback(self.brightness_changed)

    # initialize the state of the radio items
    self.brightness_changed(self.backlight.get_value())

    # create the indicator. i hope that the "gnome-brightness-applet" icon is
    # distributed with gnome by default.
    self.indicator = appindicator.Indicator("backlight-indicator",
                                            "gnome-brightness-applet",
                                            appindicator.CATEGORY_HARDWARE)
    self.indicator.set_status(appindicator.STATUS_ACTIVE)

    # show the menu
    self.menu.show()
    self.indicator.set_menu(self.menu)

  # selects the menu item associated with the given brightness value
  def get_item_for_brightness(self, value):
    index = int(round(value / 10.0))
    return self.menu_items[index]

  # callback for external changes of brightness
  def brightness_changed(self, new_value):
    new_item = self.get_item_for_brightness(new_value)
    if new_item != self.current_item:
      self.current_item = new_item
      new_item.set_active(True)

  # callback for selecting a menu item
  def item_activate(self, item, brightness_value):
    if item != self.current_item:
      self.current_item = item
      self.backlight.set_value(brightness_value)

  # cleanup
  def destroy_indicator(self):
    pass


if __name__ == "__main__":
  # tell DBus which event loop to use for signal dispatching
  # (must happen before opening the bus)
  DBusGMainLoop(set_as_default=True)

  # initialize the DBus backlight class and test it
  backlight = BacklightAdapter()
  backlight.get_value()

  indicator = IndicatorBacklight(backlight)
  gtk.main()
