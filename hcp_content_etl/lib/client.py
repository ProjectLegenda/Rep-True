import nnenv as nn
import nndw 
from creator import *

url = 'mysql+pymysql://SoftTekRead:A*USxm7BXd*&aGTS@minisitedb.chinanorth.cloudapp.chinacloudapi.cn:3306/wc_itangyi'

tar_url = 'hive://admin4PEdwc:whatever@clusternode3:10000/novodb?auth=CUSTOM'

sql_statment = ' select ln_title,ln_content,ln_date from lk_news where ln_is_valid = 1' 

file_name = 'hcp_articles.csv'

load_statment = 'LOAD DATA LOCAL INPATH \'/home/algorithm4pe/hcp_content_etl/.source_file/' +  file_name + '\' OVERWRITE INTO TABLE iqvia_hcp_articles '

etlsource = FlatCreator(product_type ='sql',source='etlsource')

etlsource.load(sqlalchemy_url = url,cursor_statment = sql_statment)

parser = FlatCreator(product_type = 'simplehtml',source = 'parser')

transformer = FlatCreator(product_type = 'simplehtmlextractor', source = 'transformer')

transformer.bind_parser(parser = parser,  key = 'ln_content')

gensource = FlatCreator(product_type = 'gen',source = 'etlsource')

gensource.load(etlsource)
gensource.bind_transformer(transformer)

gensource.dump(file_name,header = False)

etlsource.load(sqlalchemy_url = tar_url,cursor_statment = load_statment)

etlsource._execute()
