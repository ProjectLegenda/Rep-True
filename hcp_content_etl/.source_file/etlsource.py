from sqlalchemy import *
import types
import csv

import collections
from transformer import *

class Etlsource:

    def __init__(self):
        pass
        self.result = ''
        self.transformers = [] 

    def load(self,inputdata):

        if isinstance(inputdata,Etlsource):
            self.result = inputdata
        else:
            raise(TypeError)
    def bind_transformer(self,transformer):
        
        if isinstance(transformer, Transformer):
            self.transformers.append(transformer)
 
    def getdata(self):
        
        if len(self.transformers) == 0:
            for item in self.result.getdata():
                yield(item)
        
        else:
            
            for item in self.result.getdata():

                for transformer in self.transformers:
                    item = transformer.transform(item)

                yield(item)
            
                 

class Gensource(Etlsource):

    def __init__(self):
        Etlsource.__init__(self)

    def dump(self,file_name,header = True):

        with open(file_name,'w') as csv_file:
           ## header
            writer = csv.writer(csv_file)
           
            header = []
            content = []
           
            firstitem = ''
             
            gen = self.getdata()

            for item in gen:

                firstitem = item

                for key in item:
                    header.append(key)
                break;

            if header == True:
                writer.writerow(header)
            header_length = len(header)
           
            for i in range(0,header_length):
                content.append(firstitem[header[i]])

            writer.writerow(content)
           ##write content    
   
            for item in gen:
                content = []
                for i in range(0,header_length):
                    content.append(item[header[i]])     
           
                writer.writerow(content)
                
    
      
class Sqlsource(Etlsource):
    
    def __init__(self):
        Etlsource.__init__(self)

    def _bind(self,sqlalchemy_url):

        self.url = sqlalchemy_url
        self.engine = create_engine(sqlalchemy_url)
        self._statment = ''
    
    def _release(self):
        self.connection.close()

    def _cursor(self,statment):
        self._statment = statment
      
    def _execute(self):
        '''
        the fetcher only can fetch once after execution, so we need to explicitly call execute method
        '''
        self.connection = self.engine.connect()
        self.result = self.connection.execute(self._statment)
   
 
    def getdata(self):
        self._execute() 
        self._release()
        for row in self.result.fetchall():

            d = {}
            for key in row.keys():
                d[key] = row[key]
    
            yield(d)

       #return(self.data)
    def getcount(self):

        tmp = []
        self._execute()
        self._release()

        for item in self.result.fetchall():
            tmp.append(item[0])

        cnt = len(tmp)
        print(cnt)
        return(cnt)  
      
    def load(self,**kwargs):
        self.__init__()
        self._bind(kwargs['sqlalchemy_url'])
        self._cursor(kwargs['cursor_statment'])
     
