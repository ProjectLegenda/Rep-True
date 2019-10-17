#!/usr/local/bin/python3
import types


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
 

dict4 = \
    {'1':('1',),
     '11':('2',),
     '111':('3',),
     '12':(4,9),
     '112':('7',),
     '1112':('8',),
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
    
    r = '^' + reverse_str(g_r_s)      
    
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
    r = '^' + reverse_str(g_r_s)

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

    x = str(arb)
    
    if x.startswith('0') :
        return(-1)
    lst = f_split(grs)

    r = reverse_str(x) 
   
    o = str()
    for key,i in enumerate(r):

        if len(lst) < len(r):
            return(-1)
        m = f_support2(i,lst[key])
        
        if m == -1:
            return(-1)
        o = m + o 
    
    return(o)


def convert_index(input_str):
    
    r = input_str 
    f = str()
    
    m = {}
    s = 0
    for index in r:

        if index not in m.keys():
            s = s + 1
            m[index] = str(s)
            f = f + str(s)

        else:
            f = f + m[index]
    
    return(f)
 


def findAllSymbles(roman, prefix='', cnt=0, prev=''):

    if not roman:

        if prefix:

            if len(prefix) % 2 == 0 and cnt >= 2 or len(prefix) % 2 != 0 and cnt >= 4:

                tmp = list(prefix)

                tmp.insert(1, '_')

                prefix = ''.join(tmp)

            return [prefix]

        else:

            return []

    

    if roman[-1] in prefix and roman[-1] != prefix[0]:

        return []

    res = []

    if prefix and roman[-1] == prefix[0]:

        if prev[-1] == roman[-1]:        

            res += findAllSymbles(roman[:-1], prefix, cnt + 1, prev)

        else:

            res += findAllSymbles(roman[:-1], prefix, 1, roman[-1])

        if len(roman) >= 2 and roman[-2] in prefix and roman[-2] != prefix[0]:

            if prev[-1] == roman[-1]:

                res += findAllSymbles(roman[:-2], prefix, cnt + 1, prev)

            else:

                res += findAllSymbles(roman[:-2], prefix, 1, roman[-2:])

    else:

        if cnt >= 2 and len(prefix) % 2 == 0:

            tmp = list(prefix)

            tmp.insert(1, '_')

            newPrefix = ''.join(tmp)

        else:

            newPrefix = prefix

        res += findAllSymbles(roman[:-1], roman[-1] + newPrefix, 1, roman[-1])

        if len(roman) >= 2 and roman[-2] in newPrefix and newPrefix.find(roman[-2]) <= 2: 

            if (len(newPrefix) - newPrefix.find(roman[-2]) - 1) % 2 == 0:

                res += findAllSymbles(roman[:-2], roman[-1] + newPrefix, 1, roman[-2:])

            else:

                # print('{} {} {}'.format(newPrefix, roman[-2], newPrefix.find(roman[-2])))

                tmp = list(newPrefix)

                tmp.insert(1, '_')

                newPrefix = ''.join(tmp)

                res += findAllSymbles(roman[:-2], roman[-1] + newPrefix, 1, roman[-2:])

        elif len(roman) >= 2 and roman[-2] not in newPrefix and roman[-2] != roman[-1]:

            if len(newPrefix) % 2 == 0:

                res += findAllSymbles(roman[:-2], roman[-1] + roman[-2] + newPrefix, 1, roman[-2:])

            else:

                res += findAllSymbles(roman[:-2], roman[-1] + roman[-2] + '_' + newPrefix, 1, roman[-2:])      

    return res


def introspective(input_str):

    l = findAllSymbles(input_str)
    if len(l) == 0:
        return(-1)

    l2 = [ (i,perspective(input_str,i)) for i in l]

    n = -1    
    m = ''
    for item in l2:

        if item[1] != -1:
            if n == -1:
                n = item[1]
                m = item[0]
            elif n > item[1]:
                n = item[1]
                m = item[0] 
    
    if n == -1:
        return(n)

    return(n,m)



dict_syntax = \
    {'Please':
         {
             'convert':
                 {'arb':{
                         'using':{'roman':retrospective}
                         }, 
                  'string':{
                           'using':{'roman':perspective},
                           'minimally':introspective
                          }
                                       
                 }
       
         }
    }

def convert(input_str,d = dict_syntax):
    
    s = input_str.rstrip().split(' ')

    decoder = '' 

    try:

        for item in s:

            if ('arb' in d.keys()) or ('string' in d.keys()):
                if item.isdigit():
                    d = d['arb']
                    target = item 
                    continue 

                if item.isalpha():
                    d = d['string']
                    target = item
                    continue
                else:
                    return(-1)
           
            if 'roman' in d.keys():
                if item.isalpha():
                    if isunique(item):
                        f = d['roman'] 
                        decoder = item
                        return(f(target,item))   
                    else:
                        return(-1)
             
                if not item.isalpha():
                    return(-1)
            
            d = d[item]

        if isinstance(d,types.FunctionType):  
            f = d
            if len(decoder) == 0:
                return(f(target))
            else:
                return(f(target,decoder))
        else:
              
            f = d['using']['roman']
            return(f(target))
        
    except:
        return(-2)


def main():

    s = input('How can I help you? ')

    o = convert(s)
   
    if o == -1:
        print('Hey, ask me something that\'s not impossible to do!')
   
    elif o == -2:
        print('I dont\'t get what you want, sorry mate!')
    
    elif type(o) == tuple:
        print('Sure! It is {0} using {1}'.format(o[0],o[1]))

    
    else:
        print('Sure! It is {}'.format(o))
        




if __name__ == '__main__':
    main()
