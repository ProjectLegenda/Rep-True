import sqlalchemy

'''database connection'''
engine=sqlalchemy.create_engine('mysql+pymysql://root:quid0s@10.45.224.51:10086/sagacityidea_novoedaesb')
#engine=sqlalchemy.create_engine('mysql+pymysql://root:quid0s@114.215.44.212:10086/sagacityidea_novoedaesb')
