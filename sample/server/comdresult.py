# Result class used for getting result from command
# functions to be used for server
class ComdResult:
    # (if you need other variables, just add into the constructor
    # and give it a default variable)
    def __init__(self, comd="", res=""):
        self.comd = comd
        self.res = res
