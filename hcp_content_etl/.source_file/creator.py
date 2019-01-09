from etlsource import *
from parser import *
 
class EtlsourceCreator():
    
    def __init__(self,etlsource_type = 'sql'):
        
        if etlsource_type =='sql':
            self.creator = Sqletlsource
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

   def create(self):
       return(self.creator())


class CreatorCreator():

    def __init__(self,**kwargs):

        if kwargs['source'] == 'etlsource':
            self.creator = EtlsourceCreator     
            
        elif kwargs['source'] == 'parser':
            self.creator = ParserCreator
        
        else:
            raise(Exception)
     
        self.product_type = kwargs['product_type'] 

    def create(self):
        return(self.creator(self.product_type).create()) 


def FlatCreator(**kwargs):

    if kwargs['source'] == 'etlsource':
        creator = EtlsourceCreator
    
    elif kwargs['source'] == 'parser':
        creator = ParserCreator

    else:
        raise(Exception)

    product_type = kwargs['product_type']

    return(creator(product_type).create())


 
