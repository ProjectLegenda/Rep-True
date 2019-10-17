# -*- coding: utf-8 -*-

"""

Created on Mon Oct 14 16:07:11 2019



@author: think

"""



# Written by Taiping Xiang for COMP9021





def please_convert():

    input('How can I help you? ')

    print("I'll think about it...")

    # EDIT AND COMPLETE THE CODE ABOVE

import re



def createMap(roman, reversed=False):

    if not roman:

        return

    

    mapping = {roman[-1] : 1}





    val = 5

    size = len(roman)

    for i in range(2, size + 1, 1):

        if roman[size - i] != '_':

            mapping[roman[size - i]] = val

        if i % 2 == 1:

            val = val * 5

        else:

            val = val * 2

    # MDCLXVI

    for i in range(1, size, 2):

        if roman[size - i] == '_':

            continue

        if roman[size - i - 1] != '_':

            mapping[roman[size - i] + roman[size - i - 1]] = mapping[roman[size - i - 1]] - mapping[roman[size - i]]

        if roman[size - i - 2] != '_':

            mapping[roman[size - i] + roman[size - i - 2]] = mapping[roman[size - i - 2]] - mapping[roman[size - i]]



    if not reversed:

        mapping = {v : k for k, v in mapping.items()}



    return mapping



def intToRoman(num, roman='MDCLXVI'):

    mapping = createMap(roman)

    keys = sorted(mapping.keys(), reverse=True)

    

    res = ''

    while num > 0:

        for (i, key) in enumerate(keys):

            q = num // key

            if q > 0:

                num = num % key

                break

        if q == 4:

            res += mapping[key]

            res += mapping[keys[i - 1]]

        else:

            while q > 0:

                res += mapping[key]

                q -= 1

    return res



def romanToInt(num, roman='MDCLXVI'):

    mapping = createMap(roman, True)

    res = 0



    i = 0

    cnt = 0

    prev = num[0:2] if len(num) >= 2 and num[0:2] in mapping else num[0]

    while i < len(num):

        if i < len(num) - 1 and num[i:i+2] in mapping:

            if mapping[num[i:i+2]] > mapping[prev]:

                return False

            if num[i : i + 2] == prev:

                cnt += 1

            else:

                cnt = 1

            if cnt >= 2:

                return False

            res += mapping[num[i:i+2]]

            prev = num[i:i+2]

            i += 2

        else:

            if mapping[num[i]] > mapping[prev]:

                return False

            if num[i] == prev:

                cnt += 1

            else:

                cnt = 1

            if (len(roman) - roman.index(num[i])) % 2 == 0 and cnt > 2 or cnt >= 4:

                return False

            prev = num[i]

            res += mapping[num[i]]

            i += 1

    # if res >= 4000:

    #     return False

    return res



def validRoman(num):

    return re.search(r"^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", num)



def main():

    s = input('How can I help you? ')

    s += '\n'

    reg1 = re.compile('Please convert \w*\s')

    reg2 = re.compile('Please convert \w* using \w*\s')

    reg3 = re.compile('Please convert \w* minimally\s')

    

    if reg2.match(s):

        words = s.split(' ')

        if len(words) != 5:

            print('I don\'t get what you want, sorry mate!')

            return

        w1 = words[2]

        w2 = words[4].strip()

        alp = re.compile('[a-zA-Z]+')

        if (not w1.isdigit() and not set(w1).issubset(set(w2))) or not alp.match(w2) or len(set(w2)) != len(w2):

            print('Hey, ask me something that\'s not impossible to do!')

            return

        

        if w1.isdigit():

            if int(w1) <= 0 or w1.startswith('0'):

                print('Hey, ask me something that\'s not impossible to do!')

            else:

                print('Sure! It is {}'.format(intToRoman(int(w1), w2)))

        else:

            num = romanToInt(w1, w2)

            if not num:

                print('Hey, ask me something that\'s not impossible to do!')

            else:

                print('Sure! It is {}'.format(num))



    elif reg3.match(s):

        words = s.split(' ')

        if len(words) != 4:

            print('I don\'t get what you want, sorry mate!')

            return

        w = words[2].strip()

        alp = re.compile('[a-zA-Z]+')

        if not alp.match(w):

            print('Hey, ask me something that\'s not impossible to do!')

            return

        romanSymbles = findAllSymbles(w)

        res = dict()

        for symble in romanSymbles:

            val = romanToInt(w, symble)

            if w == intToRoman(val, symble):

                res[val] = symble

        

        if not res:

            print('Hey, ask me something that\'s not impossible to do!')

            return

        keys = sorted(res.keys())

        print('Sure! It is {0} using {1}'.format(keys[0], res[keys[0]]))

        



    elif reg1.match(s):

        words = s.split(' ')

        if len(words) != 3:

            print('I don\'t get what you want, sorry mate!')

            return

        w = words[2].strip()

        

        if w.isdigit():

            if int(w) >= 4000 or int(w) <= 0 or w.startswith('0'):

                print('Hey, ask me something that\'s not impossible to do!')

            else:

                print('Sure! It is {}'.format(intToRoman(int(w))))

        else:

            if validRoman(w):

                num = romanToInt(w)

                print('Sure! It is {}'.format(romanToInt(w)))

            else:

                print('Hey, ask me something that\'s not impossible to do!')

    else:

        print('I don\'t get what you want, sorry mate!')




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



if __name__ == "__main__":

    main()


