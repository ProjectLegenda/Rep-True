import pandas as pd
import numpy as np
import jieba
import re
import nndw as nn

iotype = 'db'


def createDictStop():
    """
    Load external dictionary and stop words
    """
    print("Loading Dictionary and Stopwords")
    global stopword
    
    dic = nn.Dataframefactory("mappingword",sep = '\r\n',iotype=iotype)    
    stopWord = nn.Dataframefactory("stopword",sep = '\r\n',iotype=iotype)
    
    word = dic.word.tolist()   
    stopword = stopWord.word.tolist()
    jieba.re_han_default =re.compile(r'([\u0020\u4e00-\u9fa5a-zA-Z0-9+#&._%/”/“/"/β/α/-]+)', re.UNICODE)
    
    frequnecy = 1000000000000000000000
    # Add words to dictionary
    for words in word:
        jieba.add_word(words,frequnecy)
    print("Finished Dic Loading")

def tokenize(content):
    """
    cut sentences into tokens
    """
    wordList = jieba.cut(content, cut_all=False)
    token = [word for word in wordList if (word not in stopword) and (word.strip()!="")]
    
    return token
	

def main():
    createDictStop()
    print("Loading data")
    raw = nn.Dataframefactory("pat_search",iotype = iotype)
    pat_search = raw[(raw.platform=="1")&(raw.module=="小糖问答")][["hcp_openid", "keyword"]]
    pat_search["keys"] = pat_search.keyword.apply(tokenize)
    print("Data prepared")
    
    print("Begin calculating")
    finalDf = []
    
    for index, row in pat_search.iterrows():
        keysDf = pd.DataFrame({"keyword":row["keys"]})
        keysDf["pat_search"] = row["keyword"]
        keysDf.insert(0, "pat_openid", row["hcp_openid"])
        
        finalDf.append(keysDf)
        
    output = pd.concat(finalDf, ignore_index=True)
    print("Finished calculating")
    
    nn.write_table(output,'pat_search_stats', iotype = iotype)
	# pat_search_stats structure: three columns - pat_openid, keyword, pat_search
    
    return (1)



