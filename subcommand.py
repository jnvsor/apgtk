import subprocess
from errorwindow import ErrorDialogue

class ModeError(Exception):
    pass

class ProcessStderr(ChildProcessError):
    def __init__(self, value):
        self.value = value

class CommandExecution:
    def __init__(self, binder):
        self.input = binder
    
    def execute(self):
        try:
            self.command = [str(i) for i in self.build()]
            proc = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.out, err = proc.communicate()
            if(proc.returncode):
                raise ProcessStderr(err)
        
        except ModeError:
            ErrorDialogue(  "All character types are set to disabled.",
                              "Can't create a password without characters!")
        except ProcessStderr as e:
            ErrorDialogue(  "An unforseen error occurred in the APG subprocess.",
                            "stderr output:\n" + e.value.decode())
        except FileNotFoundError:
            ErrorDialogue(  "APG is not installed!","Please install apg through your "
                            "package manager.")
        except Exception as e:
            ErrorDialogue(  "An unforseen error occurred.", 
                str(type(e).__name__) + ": " + str(e))
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
        
        amount = ["-n", int(self.input["amount"].get_value())]
        min = ["-m", self.input["length"].get_min()]
        max = ["-x", self.input["length"].get_max()]
        
        seed, exclude, dictionary, mode, crypt, phone, pronouncedisplay = ([] for x in range(7))
        
        if(self.input["seed"].get_enabled()):
            seed = ["-c", self.input["seed"].get_value()]
        
        if(self.input["exclude"].get_enabled()):
            exclude = ["-E", self.input["exclude"].get_value()]
        
        if(self.input["dictionary"].get_enabled()):
            dictionary = ["-r", self.input["dictionary"].get_value()]
        
        for index, key in enumerate(sorted(self.input["mode"].widgets.keys())):
            if(self.input["mode"].widgets[key].get_value() == 1):
                mode += chr(ord(key)+32)
            elif(self.input["mode"].widgets[key].get_value() == 2):
                mode += key
        
        if(mode == []):
            if self.input["algorithm"].get_value():
                raise ModeError
            """ Pronunciation mode ignores mode setting anyway, but will balk at
            an empty mode setting, so we default but throw exception for random mode """
            mode = ["c", "l", "n", "s"]
        
        mode = ["-M", "".join(mode)]
        
        algorithm = ["-a", self.input["algorithm"].get_value()]
        if not self.input["algorithm"].get_value():
            pronouncedisplay = ["-t"]
        
        if(self.input["crypt"].get_active()):
            crypt = ["-y"]
        
        if(self.input["phone"].get_active()):
            phone = ["-l"]
        
        return  command+algorithm+mode+exclude+amount+min+max+\
                dictionary+seed+crypt+phone+pronouncedisplay
