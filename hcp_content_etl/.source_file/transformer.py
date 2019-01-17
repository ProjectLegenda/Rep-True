import types
from etlsource import *

class Transformer():
      
    def __init__(self):
        pass

    def bind_parser(self,**kwargs):
        pass

    def transform(self,input_dict):
        return(input_dict)
 
class HTMLdataextractor(Transformer):

    def __init__(self):
        pass

    def bind_parser(self,**kwargs):
           
        self.parser = kwargs['parser']
        self.key = kwargs['key']

    def transform(self,input_dict):

        d = {}
            
        for key in input_dict:
            if key == self.key:
                self.parser.feed(input_dict[key])           
                tmp = self.parser.getdata() 
                d[key] = tmp
            else:
                d[key] = input_dict[key]  
        
        return(d)

