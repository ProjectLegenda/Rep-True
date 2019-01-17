from sqlalchemy import *

class Loader():

    def __init__(self):
        pass

    def bind(self,url):
        pass

    def load(self,etlsouce):
        pass




class Sqlloader(Loader):
  
    def _bind(self,sqlalchemy_url):
        self.url = sqlalchemy_url
        self.engine = create_engine(sqlalchemy_url)
        self._statment = ''     


    def _release(self):
        self.connection.close()
    
    def _cursor(self,statment)
        self._statment = statment

    def _execute(self):
        self.connection = self.engine.connect()
        self.result = self.connection.execute(self._statment) 


    def load(self,**kwargs):
        self.__init__()
        self._bind(kwargs['sqlalchemy_url'])
        self._cursor(kwargs['cursor_statment'])


    def getdata(self):
        self._execute()
        self._release()
        for row in self.result.fetchall():
            d = {}
            for key in row.keys():
                d[key] = row[key]
            
             yield(d)
