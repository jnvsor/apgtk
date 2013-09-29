#!/usr/bin/python3
from gi.repository import Gtk
from mainwindow import MainWindow
from subcommand import CommandBuilder

win = MainWindow()
win.bind_builder(CommandBuilder())
win.show()
Gtk.main()

""" Apg bugs to work around:
* Runs infinitely given impossible options - seems to be fixed with a hack in
    APG itself that sets all characters to 'a' when this happens.
* Space in seed value prints help file (hacked around it - stripping spaces on focus out)
* APG doesn't generate spaces so it presumes a space is there by accident and
    messes up the command if spaces are the only thing in the exclusion (Same hack)"""
