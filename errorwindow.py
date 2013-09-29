from gi.repository import Gtk

class ErrorDialogue(Gtk.MessageDialog):
    def __init__(self, message, details=None):
        Gtk.MessageDialog.__init__(self,0,Gtk.DialogFlags.MODAL,Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, message, title="An error occurred!")
        
        if details:
            self.format_secondary_text(details)
        
        self.run()
        self.destroy()
