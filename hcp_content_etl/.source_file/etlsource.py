from sqlalchemy import *

class Etlsource():

   def __init__(self):
       pass

   def load(self,inputdata):

       if isinstance(inputdata,list): 
           self.result = inputdata
       else:
           raise(TypeError)
       
   def getdata(self):
       for item in self.result:
           yield(item)

class Sqletlsource(Etlsource):
    
    def __init__(self):
        Etlsource.__init__(self)

    def bind(self,sqlalchemy_url):

        self.url = sqlalchemy_url
        self.engine = create_engine(sqlalchemy_url)
        self.engine.connect()
        self.cursor_statment = ''
     
    def _cursor(self,cursor_statment):
        self.cursor_statment = cursor_statment
      
    def execute(self,cursor_statment):
        '''
        the fetcher only can fetch once after execution, so we need to explicitly call execute method
        '''
        self._cursor(cursor_statment)
        self.result =  self.engine.execute(self.cursor_statment)

    def getdata(self):
        self.execute(self.cursor_statment) 
        for item in self.result.fetchall():
            yield(item)
       #return(self.data)
    def getcount(self):

        tmp = []
        self.execute(self.cursor_statment)

        for item in self.result.fetchall():
            tmp.append(item[0])

        cnt = len(tmp)
        print(cnt)
        return(cnt)  
      
    def load(self,**kwargs):
        self.__init__()
        self.bind(kwargs['sqlalchemy_url'])
        self.execute(kwargs['cursor_statment'])
 
