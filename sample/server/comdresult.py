# Result class used for getting result from command
# functions to be used for server
class ComdResult:
    # (if you need other variables, just add into the constructor
    # and give it a default variable)
    def __init__(self, comd="", res="", res1="", res2="", res3=""):
        self.comd = comd
        self.res = res
        self.res1 = res1
        self.res2 = res2
        self.res3 = res3
