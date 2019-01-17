from etlsource import *
from parser import *
from transformer import *

class EtlsourceCreator():
    
    def __init__(self,etlsource_type = 'sql'):
        
        if etlsource_type =='sql':
            self.creator = Sqlsource
        elif etlsource_type =='gen':
            self.creator = Gensource
        elif etlsource_type =='ori':
            self.creator = Etlsource
        else:
            print('Invalid etl source type')
            raise(Exception) 

    def create(self):
        return(self.creator())


class ParserCreator():

   def __init__(self,parser_type = 'simplehtml'):

       if parser_type == 'simplehtml':
           self.creator = SimpleHTMLparser 

       else:
           print('Invalid parser_type')
           raise(Exception)
             
   def create(self):
       return(self.creator())

class TransformerCreator():
    
    def __init__(self,product_type = 'simplehtmlextractor'):
     
        if product_type == 'simplehtmlextractor':
            self.creator = HTMLdataextractor
        else:
            print('Invalid transformer type')
            raise(Exception)
       
    def create(self):
        return(self.creator())

class CreatorCreator():

    def __init__(self,**kwargs):

        if kwargs['source'] == 'etlsource':
            self.creator = EtlsourceCreator     
            
        elif kwargs['source'] == 'parser':
            self.creator = ParserCreator
        
        elif kwargs['source'] == 'transformer':
            self.creator = TransformerCreator
        else:
            raise(Exception)
     
        self.product_type = kwargs['product_type'] 

    def create(self):
        return(self.creator(self.product_type).create()) 


def FlatCreator(**kwargs):

    creator = CreatorCreator(**kwargs)

    return(creator.create())


 
