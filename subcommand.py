import subprocess

class ModeError(Exception):
    def __init__(self, value):
        self.value = value


class SubprocessError(Exception):
    def __init__(self, value):
        self.value = value


class CommandBuilder:
    def __init__(self):
        self.bound = False
        pass
    
    def bind(self,inputdevice):
        for value in ["amount", "length", "seed", "exclude", "dictionary", "filter", "mode", "algorithm", "crypt", "phone"]:
            setattr(self,value,getattr(inputdevice,value))
        self.bound = True
    
    def build(self):
        if not self.bound:
            exit("Fatal error: Unbound CommandBuilder. This should not have happened.")
            return
        
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


class CommandExecution:
    def __init__(self, command):
        self.command = [str(i) for i in command]
        
        self.proc = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self.out, self.err = self.proc.communicate()
        if(self.proc.returncode):
            raise SubprocessError(self.err)


class OutputParser:
    def raw(execution):
        command = execution.command
        data = execution.out
        
        passwords = []
        
        for line in data.decode("utf-8").split("\n"):
            line = line.split()
            
            if(line == []):
                continue
            
            linedict = {"Password": line.pop(0)}
            
            if("-t" in command):
                linedict["Pronunciation"] = line.pop(0)[1:-1]
            
            if("-y" in command):
                linedict["Crypt"] = line.pop(0)
            
            if("-l" in command):
                linedict["Phonetics"] = line.pop(0)
            
            passwords.append(linedict)
            
        return passwords