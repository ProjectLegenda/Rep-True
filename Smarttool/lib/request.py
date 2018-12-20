class Request():
    def __init__(self,r_seq,r_data,r_type):
        self.r_seq = r_seq
        self.r_data = r_data
        self.r_type = r_type
        if self.r_type not in ['RELOAD','CALCULATE','SHUTDOWN','TEST']:
            print('[ERROR]Invalid request type')
            raise ValueError
        
    def rtype(self):
        return(self.r_type)
    
    def rdata(self):
        return(self.r_data)
   
    def rseq(self):
        return(self.r_seq)



        
