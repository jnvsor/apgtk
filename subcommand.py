import subprocess
from errorwindow import ErrorDialogue

class ModeError(Exception):
    def __init__(self, value):
        self.value = value

class ProcessStderr(ChildProcessError):
    def __init__(self, value):
        self.value = value

class CommandExecution:
    def execute(self):
        try:
            self.command = [str(i) for i in self.build()]
            proc = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.out, err = proc.communicate()
            if(proc.returncode):
                raise ProcessStderr(err)
        
        except ModeError as e:
            if e.value == []:
                ErrorDialogue(  "All character types are set to disabled.",
                                "Can't create a password without characters!")
            else:
                ErrorDialogue(  "An unforseen error occurred concerning the character "
                                "type checkboxes.", "Mode contents:\n" + str(e.value))
        except ProcessStderr as e:
            ErrorDialogue(  "An unforseen error occurred in the APG subprocess.",
                            "stderr output:\n" + str(e.value))
        except Exception as e:
            if(isinstance(e,IOError) and str(e)[-5:] == "'apg'"):
                ErrorDialogue(  "APG is not installed!","Please install apg through your "
                                "package manager.")
            else:
                ErrorDialogue(  "An unforseen error occurred.", str(e))
        else:
            return True
    
    def as_list(self):
        passwords = []
        
        for line in self.out.decode("utf-8").split("\n"):
            line = line.split()
            
            if(line == []):
                continue
            
            linedict = {"Password": line.pop(0)}
            if("-t" in self.command):
                linedict["Pronunciation"] = line.pop(0)[1:-1]
            if("-y" in self.command):
                linedict["Crypt"] = line.pop(0)
            if("-l" in self.command):
                linedict["Phonetics"] = line.pop(0)
            
            passwords.append(linedict)
            
        return passwords
    
    def build(self):
        command = ["apg"]
        amount = ["-n", int(self.amount.get_value())]
        min = ["-m", self.length.get_min()]
        max = ["-x", self.length.get_max()]
        
        seed, exclude, dictionary, filter, mode, crypt, phone, pronouncedisplay = ([] for x in range(8))
        
        if(self.seed.get_enabled()):
            seed = ["-c", self.seed.get_value()]
        
        if(self.exclude.get_enabled()):
            exclude = ["-E", self.exclude.get_value()]
        
        if(self.dictionary.get_enabled()):
            dictionary = ["-r", self.dictionary.get_value()]
        
        if(self.filter.get_enabled()):
            filter = ["-b", self.filter.get_value()]
        
        for index, key in enumerate(sorted(self.mode.widgets.keys())):
            if(self.mode.widgets[key].get_value() == 1):
                mode += chr(ord(key)+32)
            elif(self.mode.widgets[key].get_value() == 2):
                mode += key
        
        if(mode == []):
            if self.algorithm.get_value():
                raise ModeError(mode)
            """ Pronunciation mode ignores mode setting anyway, but will balk at
            an empty mode setting, so we default but throw exception for random mode """
            mode = ["c", "l", "n", "s"]
        
        mode = ["-M", "".join(mode)]
        
        algorithm = ["-a", self.algorithm.get_value()]
        if not self.algorithm.get_value():
            pronouncedisplay = ["-t"]
        
        if(self.crypt.get_active()):
            crypt = ["-y"]
        
        if(self.phone.get_active()):
            phone = ["-l"]
        
        return  command+algorithm+mode+exclude+amount+min+max+\
                dictionary+filter+seed+crypt+phone+pronouncedisplay
