#!/usr/local/bin/python3

dict2 = \
    {1:
          {1:
                {1:{2:{0:8},0:3},
                 2:{0:7},
                 0:2
                },
           2:
                {0:6},
           0:1
          },
     2:
          {1:
                {0:4},
           0:5
          },
     3:   {1:
             {0:9},
           0:0
          },
     0:0
    }


dict3 = \
    {'0':'',
     '1':'1',
     '2':'11',
     '3':'111',
     '4':'12',
     '5':'2',
     '6':'21',
     '7':'211',
     '8':'2111',
     '9':'13'
     }
 

def isunique(input_str):

    if type(input_str) == str:  
        t = [i for i in input_str]
    elif type(input_str) == list:
        t = input_str

    x = []

    for i in t:
        if x.count(i) == 0:
            x.append(i)
    
    if x == t:
        return(True) 
    else:
        return(False)
    
def reverse_str(input_str):
    t = [i for i in input_str]
    t.reverse()
    x = ''
    for item in t:
        x = x + item 
    return(x)

def f_support(g_r_n,g_r_s,d = dict2):
    
    r = '0' + reverse_str(g_r_s)      
    
    t = reverse_str(g_r_n)
    
    i = 0

    switch = 0
    for item in t:

       
        try:
            x = r.index(item)

            if x == 3:
                switch = switch + 1

        except ValueError:
            
            if switch in (1,2):
                return(d[0],i-1,-1)

            return(d[0],i,-1)
            

        if x in d.keys():

            d = d[x]
            i = i + 1

        else: 
           if switch == 2:
               return(d[0],i-1,-1)   
           return(d[0],i,-1)

        if len(d) == 1 :
            return(d[0],i,1)


    if x == 3:
        return(d[0],i-1,0)

    return(d[0],i,0)

    





def f_support2(arb,g_r_s,d=dict3):
    
    o = ''
    r = '0' + reverse_str(g_r_s)

    try:
        ser = dict3[str(arb)]
    
        for i in ser:
            o = o + r[int(i)]
    except:
        return(-1)

    return(o)
    

def f_split(input_str,step = 2):
    
    l = len(input_str)
    t = []
    for i in range(l-1,-step,-step):
        
        x = i-step
        if x < 0:
            x = 0
        t.append(input_str[x:i+1])
    
    return(t)

def perspective(grn,grs = 'MDCLXVI'):

    if not isunique(grs):
        return(-1)

    lst = f_split(grs)
    
    l2 = len(grn)
    
    grn_start_point = l2    

    exp = 0 
    
    n = 0

    for i in lst:
       
        if len(grn[:grn_start_point]) == 0 :
            return(n)

        a,b,c = f_support(grn[:grn_start_point],i)
        
#        print(grn[:grn_start_point],i) 
#        print(a,b,c)
        grn_start_point = grn_start_point - b 
        n = a*(10**exp) + n
        exp = exp + 1
  #      print(grn_start_point)
        
    if c == -1:
        return(-1)


    return(n) 
        
      
def retrospective(arb,grs = 'MDCLXVI'):

    if not isunique(grs):
        return(-1)

    x = str(arb)
 
    lst = f_split(grs)

    r = reverse_str(x) 
   
    o = str()
    for key,i in enumerate(r):

        m = f_support2(i,lst[key])
        
        if m == -1:
            return(-1)
        o = m + o 
    
    return(o)


     



if __name__ == '__main__':
    print(1)
