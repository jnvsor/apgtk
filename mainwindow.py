from gi.repository import Gtk
from subcommand import CommandExecution
from outputwindow import OutputWindow

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Automated Password Generator")
        
        self.set_border_width(5)
        self.set_has_resize_grip(False)
        self.set_resizable(False)
        self.connect("delete-event", Gtk.main_quit)
        
        grid = Gtk.Grid(column_spacing=10, row_spacing=5)
        
        amount = AmountInput()
        amount.attach_to_grid(grid, 0, 0)
        
        length = LengthInput()
        length.attach_to_grid(grid, 0, 1)
        
        seed = CheckAndText("Seed value",
            "The seed value adds an extra bit of randomness to the generated password.\n"
            "Enter random text to seed your generated password.")
        seed.entry.set_max_length(16)
        seed.attach_to_grid(grid, 0, 2)
        
        exclude = CheckAndText("Exclude characters",
            "Characters to exclude from the generated password.")
        exclude.attach_to_grid(grid, 0, 3)
        
        dictionary = CheckAndFile("Use dictionary file")
        dictionary.attach_to_grid(grid, 0, 4)
        
        mode = ModeInput()
        mode.attach_to_grid(grid, 0, 6)
        
        algorithm = AlgorithmRadios()
        algorithm.attach_to_grid(grid, 0, 9)
        
        grid.attach(Gtk.Label(label="Display Options"), 0, 12, 2, 1)
        
        crypt = Gtk.CheckButton(label="Crypted")
        crypt.set_tooltip_text("Additionally pass generated passwords through crypt().")
        grid.attach(crypt, 0, 13, 1, 1)
        
        phone = Gtk.CheckButton(label="Phonetical")
        phone.set_tooltip_text("Additionally show the passwords phonetically.")
        grid.attach(phone, 1, 13, 1, 1)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.pack_start(grid,True,True,0)
        
        box.pack_start(Gtk.Separator(),True,True,0)
        
        buttons = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        buttons.set_layout(Gtk.ButtonBoxStyle.END)
        box.pack_start(buttons,True,True,0)
        
        generate = Gtk.Button(label="Generate", image=Gtk.Image(stock=Gtk.STOCK_OK))
        generate.connect("clicked", self.generate)
        buttons.pack_start(generate, True, True, 0)
        
        quitbutton = Gtk.Button(stock=Gtk.STOCK_QUIT)
        quitbutton.connect("clicked", Gtk.main_quit)
        buttons.pack_start(quitbutton, True, True, 0)
        
        self.add(box)
        box.show_all()
        
        bind = locals()
        bind = { key: bind[key] for key in [
                "amount", "length", "seed", "exclude", "dictionary",
                "mode", "algorithm", "crypt", "phone" ]
        }
        self.exec = CommandExecution(bind)
    
    def generate(self, widget):
        if self.exec.execute():
            win = OutputWindow(self.exec.as_list())
            win.set_transient_for(self)
            win.show()

class DoubleColumn:
    def __init__(self, left, right):
        self.leftcolumn = left
        self.rightcolumn = right
        
        self.leftcolumn.set_halign(Gtk.Align.START)
        self.rightcolumn.set_hexpand(True)
        self.rightcolumn.set_halign(Gtk.Align.FILL)
    
    def attach_to_grid(self, grid, left, top):
        grid.attach(self.leftcolumn, left, top, 1, 1)
        grid.attach(self.rightcolumn, left+1, top, 1, 1)

class AmountInput(DoubleColumn):
    def __init__(self):
        label = Gtk.Label(label="Amount to generate:")
        self.adjustment = Gtk.Adjustment.new(10,1,100,1,10,0)
        widget = Gtk.SpinButton()
        widget.set_adjustment(self.adjustment)
        self.adjustment.value_changed()
        
        DoubleColumn.__init__(self, label, widget)
    
    def get_value(self):
        return self.adjustment.get_value()

class LengthInput(DoubleColumn):
    def __init__(self):
        label = Gtk.Label(label="Length between:")
        box = Gtk.Box(spacing=5)
        box.set_homogeneous(True)
        
        self.adjust1 = Gtk.Adjustment.new(10,8,100,1,10,0)
        widget1 = Gtk.SpinButton()
        widget1.set_adjustment(self.adjust1)
        self.adjust1.value_changed()
        
        self.adjust2 = Gtk.Adjustment.new(15,8,100,1,10,0)
        widget2 = Gtk.SpinButton()
        widget2.set_adjustment(self.adjust2)
        self.adjust2.value_changed()
        
        box.pack_start(widget1,True,True,0)
        box.pack_start(widget2,True,True,0)
        
        DoubleColumn.__init__(self, label, box)
    
    def get_min(self):
        return int(min(self.adjust1.get_value(), self.adjust2.get_value()))
    
    def get_max(self):
        return int(max(self.adjust1.get_value(), self.adjust2.get_value()))

class TriStateCheckButton(Gtk.CheckButton):
    def __init__(self, name):
        self.name = name
        Gtk.CheckButton.__init__(self, label=self.name)
        
        self.connect("toggled",self.toggled)
        ''' Triggers the toggled callback and actually
        sets the value to inconsistent (The third state) '''
        self.set_active(True)
    
    ''' Getting this function to work was a royal pain in the arse. The toggle
    event (and likewise the click, activate etc events) allow the user to change
    the checkbutton value before the callback gets it's hands on it. I don't
    remember how I figured this logic knot out before (brute force programming?)
    but I'm glad I still have my old source code around, and lucky that it works
    with gtk3... '''
    def toggled(self, widget):
        if(self.get_inconsistent()):
            self.set_active(True)
            self.set_inconsistent(False)
            self.set_tooltip_text(self.name + " will be required")
        elif(self.get_active()):
            self.set_inconsistent(True)
            self.set_tooltip_text(self.name + " might be generated")
        else:
            self.set_tooltip_text(self.name + " will not be generated")
    
    def get_value(self):
        if(self.get_inconsistent()):
            return 1
        elif(self.get_active()):
            return 2
        else:
            return 0

class ModeInput(DoubleColumn):
    def __init__(self):
        self.label = Gtk.Label(label="Characters to Generate")
        
        self.widgets = {}
        for flag, name in [("C", "Capital letters"),
                           ("L", "Small letters"),
                           ("N", "Numbers"),
                           ("S", "Symbols")]:
            self.widgets[flag] = TriStateCheckButton(name)
    
    def attach_to_grid(self, grid, left, top):
        grid.attach(self.label, left, top, 2, 1)
        for index, widget in enumerate(sorted(self.widgets.keys())):
            grid.attach(self.widgets[widget], index%2+left, index/2+top+1, 1, 1)

class CheckAndValue(DoubleColumn):
    def __init__(self, check, widget):
        self.check = Gtk.CheckButton(label=check+":")
        DoubleColumn.__init__(self, self.check, widget)
    
    def get_enabled(self):
        return bool(self.check.get_active() and self.get_value())

class CheckAndText(CheckAndValue):
    def __init__(self, label, tooltip):
        self.entry = Gtk.Entry()
        self.entry.set_tooltip_text(tooltip)
        self.entry.connect("focus-out-event", self.stripspaces)
        
        CheckAndValue.__init__(self, label, self.entry)
    
    def get_value(self):
        return self.entry.get_text()
    
    def stripspaces(self, widget, data):
        self.entry.set_text(self.entry.get_text().replace(" ",""))

class CheckAndFile(CheckAndValue):
    def __init__(self, label):
        self.file = Gtk.FileChooserButton(Gtk.FileChooserAction.OPEN)
        CheckAndValue.__init__(self, label, self.file)
    
    def get_value(self):
        return self.file.get_filename()

class AlgorithmRadios(DoubleColumn):
    def __init__(self):
        self.label = Gtk.Label(label="Generation Algorithm")
        self.left = Gtk.RadioButton(label="Random")
        self.right = Gtk.RadioButton(group=self.left, label="Pronounceable")
    
    def attach_to_grid(self, grid, left, top):
        grid.attach(self.label, left, top, 2, 1)
        grid.attach(self.left, left, top+1, 1, 1)
        grid.attach(self.right, left+1, top+1, 1, 1)
    
    def get_value(self):
        return int(self.left.get_active())
