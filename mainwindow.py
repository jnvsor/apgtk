from gi.repository import Gtk
from subcommand import CommandExecution, SubprocessError, ModeError, OutputParser
from outputwindow import OutputWindow
from errorwindow import ErrorDialogue

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Automated Password Generator")
        
        self.set_border_width(5)
        self.set_has_resize_grip(False)
        self.set_resizable(False)
        
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(5)
        
        self.amount = AmountInput()
        self.amount.attach_to_grid(self.grid, 0, 0)
        
        self.length = LengthInput()
        self.length.attach_to_grid(self.grid, 0, 1)
        
        self.seed = SeedInput()
        self.seed.attach_to_grid(self.grid, 0, 2)
        
        self.exclude = ExcludeInput()
        self.exclude.attach_to_grid(self.grid, 0, 3)
        
        self.dictionary = DictionaryInput()
        self.dictionary.attach_to_grid(self.grid, 0, 4)
        
        self.filter = FilterInput()
        self.filter.attach_to_grid(self.grid, 0, 5)

        self.mode = ModeInput()
        self.mode.attach_to_grid(self.grid, 0, 6)
        
        self.algorithm = AlgorithmRadios()
        self.algorithm.attach_to_grid(self.grid, 0, 9)
        
        
        self.grid.attach(Gtk.Label(label="Display Options"), 0, 12, 2, 1)
        
        self.crypt = Gtk.CheckButton(label="Crypted")
        self.crypt.set_tooltip_text("Additionally pass generated passwords through crypt().")
        self.grid.attach(self.crypt, 0, 13, 1, 1)
        
        self.phone = Gtk.CheckButton(label="Phonetical")
        self.phone.set_tooltip_text("Additionally show the passwords phonetically.")
        self.grid.attach(self.phone, 1, 13, 1, 1)
        
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.box.pack_start(self.grid,True,True,0)
        
        self.box.pack_start(Gtk.Separator(),True,True,0)
        
        self.buttons = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        self.buttons.set_layout(Gtk.ButtonBoxStyle.END)
        self.box.pack_start(self.buttons,True,True,0)
        
        self.generate = GenerateButton()
        self.buttons.pack_start(self.generate, True, True, 0)
        
        self.quitbutton = QuitButton()
        self.buttons.pack_start(self.quitbutton, True, True, 0)
        
        self.add(self.box)
        self.box.show_all()
        
        self.connect("delete-event", Gtk.main_quit)
        
    def bind_builder(self, builder):
        builder.bind(self)
        self.generate.builder = builder


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
        self.label = Gtk.Label(label="Amount to generate:")
        self.adjustment = Gtk.Adjustment(10,1,100,1,10,0)
        self.widget = Gtk.SpinButton()
        self.widget.set_adjustment(self.adjustment)
        self.adjustment.value_changed()
        
        DoubleColumn.__init__(self, self.label, self.widget)
    
    def get_value(self):
        return self.adjustment.get_value()


class LengthInput(DoubleColumn):
    def __init__(self):
        self.label = Gtk.Label(label="Length between:")
        self.box = Gtk.Box(spacing=5)
        self.box.set_homogeneous(True)
        
        self.adjust1 = Gtk.Adjustment(10,8,100,1,10,0)
        self.adjust2 = Gtk.Adjustment(15,8,100,1,10,0)
        
        self.widget1 = Gtk.SpinButton()
        self.widget1.set_adjustment(self.adjust1)
        self.adjust1.value_changed()
        self.widget2 = Gtk.SpinButton()
        self.widget2.set_adjustment(self.adjust2)
        self.adjust2.value_changed()
        
        self.box.pack_start(self.widget1,True,True,0)
        self.box.pack_start(self.widget2,True,True,0)
        
        DoubleColumn.__init__(self, self.label, self.box)
        
    def get_min_max_value(self):
        if(self.adjust1.get_value() <= self.adjust2.get_value()):
            return (self.adjust1.get_value(), self.adjust2.get_value())
        else:
            return (self.adjust2.get_value(), self.adjust1.get_value())
    
    def get_min(self):
        return int(self.get_min_max_value()[0])
    
    def get_max(self):
        return int(self.get_min_max_value()[1])


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
        for flag, name in [("C", "Capital letters"), ("L", "Small letters"), ("N", "Numbers"), ("S", "Symbols")]:
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


class SeedInput(CheckAndText):
    def __init__(self):
        CheckAndText.__init__(self, "Seed value",
            "The seed value adds an extra bit of randomness to the generated password.\n"
            "Enter random text to seed your generated password.")
        self.entry.set_max_length(16)


class ExcludeInput(CheckAndText):
    def __init__(self):
        CheckAndText.__init__(self, "Exclude characters",
            "Characters to exclude from the generated password.")


class CheckAndFile(CheckAndValue):
    def __init__(self, label):
        self.file = Gtk.FileChooserButton(Gtk.FileChooserAction.OPEN)
        
        CheckAndValue.__init__(self, label, self.file)
    
    def get_value(self):
        return self.file.get_filename()


class DictionaryInput(CheckAndFile):
    def __init__(self):
        CheckAndFile.__init__(self, "Use dictionary file")


class FilterInput(CheckAndFile):
    def __init__(self):
        CheckAndFile.__init__(self, "Use filter file")


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


class GenerateButton(Gtk.Button):
    def __init__(self):
        Gtk.Button.__init__(self, label="Generate", image=Gtk.Image(stock=Gtk.STOCK_OK))
        self.connect("clicked", self.clicked)
        
    def clicked(self, widget):
        if not self.builder:
            exit("Fatal error: Unbound GenerateButton. This should not have happened.")
        
        try:
            executed = CommandExecution(self.builder.build())
        except ModeError as e:
            if e.value == []:
                ErrorDialogue(  "All character types are set to disabled.",
                                "Can't create a password without characters!")
            else:
                ErrorDialogue(  "An unforseen error occurred concerning the character "
                                "type checkboxes.", "Mode contents:\n" + str(e.value))
        except SubprocessError as e:
            ErrorDialogue(  "An unforseen error occurred in the APG subprocess.",
                            "stderr output:\n" + str(e.value))
        except Exception as e:
            if(isinstance(e,IOError) and str(e)[-5:] == "'apg'"):
                ErrorDialogue(  "APG is not installed!","Please install apg through your "
                                "package manager.")
            else:
                ErrorDialogue(  "An unforseen error occurred.", str(e))
        else:
            win = OutputWindow(OutputParser.raw(executed))
            win.set_transient_for(self.get_toplevel())
            win.show()
    

class QuitButton(Gtk.Button):
    def __init__(self):
        Gtk.Button.__init__(self, stock=Gtk.STOCK_QUIT)
        self.connect("clicked", Gtk.main_quit)

