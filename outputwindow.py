from gi.repository import Gtk

class OutputWindow(Gtk.Window):
    def __init__(self, data):
        Gtk.Window.__init__(self, title="Passwords Generated")
        
        self.set_border_width(5)
        self.set_modal(True)
        self.set_has_resize_grip(False)
        
        self.model = PasswordModel(data)
        self.view = PasswordView(self.model,data)
        
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.add(self.view)
        self.scroll.set_min_content_height(270)
        self.scroll.set_min_content_width(600)
        
        self.add(self.scroll)
        self.scroll.show_all()


class PasswordModel(Gtk.ListStore):
    def __init__(self, data):
        Gtk.ListStore.__init__(self,*[str] * len(data[0]))
        
        for row in data:
            insert = [row["Password"]]
            
            for i in ["Pronunciation", "Crypt", "Phonetics"]:
                if(i in row):
                    insert.append(row[i])
            
            self.append(insert)


class PasswordView(Gtk.TreeView):
    def __init__(self, model, data):
        Gtk.TreeView.__init__(self, model)
        
        index = 0
        for name in ["Password", "Pronunciation", "Crypt", "Phonetics"]:
            if name not in data[0].keys():
                continue
            
            renderer = Gtk.CellRendererText()
            renderer.set_property("editable", True)
            column = Gtk.TreeViewColumn(name, renderer, text=index)
            index+=1
            self.append_column(column)
