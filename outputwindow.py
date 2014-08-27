from gi.repository import Gtk

class OutputWindow(Gtk.Window):
    def __init__(self, data):
        Gtk.Window.__init__(self, title="Passwords Generated")
        
        self.set_border_width(5)
        self.set_modal(True)
        self.set_has_resize_grip(False)
        
        model = PasswordModel(data)
        view = PasswordView(model,data)
        
        scroll = Gtk.ScrolledWindow()
        scroll.add(view)
        scroll.set_min_content_height(270)
        scroll.set_min_content_width(600)
        
        self.add(scroll)
        scroll.show_all()

class PasswordModel(Gtk.ListStore):
    def __init__(self, data):
        Gtk.ListStore.__init__(self,*[str] * len(data[0]))
        
        for row in data:
            insert = []
            
            for i in ["Password", "Crypt", "Pronunciation", "Phonetics"]:
                if(i in row):
                    insert.append(row[i])
            
            self.append(insert)

class PasswordView(Gtk.TreeView):
    def __init__(self, model, data):
        Gtk.TreeView.__init__(self, model)
        
        index = 0
        copyRenderer = Gtk.CellRendererText(editable=True)
        immuteRenderer = Gtk.CellRendererText()
        
        for name in ["Password", "Crypt", "Pronunciation", "Phonetics"]:
            if name not in data[0].keys():
                continue
            
            renderer = copyRenderer
            if name in ["Pronunciation", "Phonetics"]:
                renderer = immuteRenderer
            
            column = Gtk.TreeViewColumn(name, renderer, text=index)
            index+=1
            self.append_column(column)
