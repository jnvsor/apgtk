#!/usr/bin/python3
import signal
from gi.repository import Gtk
from mainwindow import MainWindow

signal.signal(signal.SIGINT, signal.SIG_DFL)
win = MainWindow()
win.show()
Gtk.main()