import pandas as pd

class Transformer:

    def __init__(self,df):
        ## check keys

        key_list = ['strength','doctor_id','content_id','method']

        for key in key_list:
            
            if key not in df.columns:
                raise (KeyError, "Input dataframe should have at least following keys strength,doctor_id,content_id,method ")

        
        self.df = df

        self.setParames()


    def setDataframe(self,df):
        self.__init__(df)
        

    def setParames(self,n=5,inplace=False):  

        '''
        get Maxmiun records

        '''
        self.max_records = n
        self.inplace=inplace

    def transform(self):
       

        df_temp = self.df.sort_values(axis=0,by=['doctor_id','strength'],ascending=[True,False])
        df_temp['xn1'] = df_temp.groupby('doctor_id').cumcount() + 1
        df_temp = df_temp[df_temp['xn1']<=self.max_records]

        
        lu = self.df['doctor_id'].drop_duplicates().tolist()

        nu = []

        for d in lu:
            nu = nu + [{'doctor_id':d,'xn1':i + 1} for i in range (0,self.max_records)]

        rdf = pd.DataFrame(nu).merge(df_temp,on=['doctor_id','xn1'],how='left')

        if self.inplace:
            self.df = rdf 

        return(rdf)

    def __str__(self):
        return(self.transform().__str__())

    def getDataframe(self):
            return(self.transform())


        


