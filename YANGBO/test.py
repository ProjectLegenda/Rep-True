
from practice import f_support
from practice import perspective
from practice import f_split
from practice import retrospective
from practice import reverse_str
from practice import convert_index


#print(f_split('MDCLXVI'))
#print(f_split('abcdedfhi'))

#print('UNIQUE TEST')
#print(perspective('123','IIV'))


#print('PERSPECTIVE TEST')
print(perspective('XXIX'))
print(retrospective(49))
#print(perspective('XVII'))
#print(perspective('MCMLXXXII'))
#print(perspective(grn='M',grs='MDCLXVI'))
#print(perspective(grn='EeDEBBBaA',grs='fFeEdDcCbBaA'))
#print(perspective(grn='ABCDEFGHIJKLMNOPQRST',grs='AbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStT'))
#print(perspective(grn='IIII'))
#print(perspective(grn='AMAZING',grs='LAQMPVXYZIRSGN'))
#print(perspective('VI'))


#print(retrospective(3999,'MDCLXVI'))

#print(retrospective(1900604,'LAQMPVXYZIRSGN'))
#print(retrospective('899999999999','AaBbCcDdEeFfGgHhIiJjKkLl'))



'''
for i in range(1,4000):
    x = retrospective(i)
    m = perspective(x)

    if i != m:
        print(i,x,m)
'''


#print(convert_index('ABCD'))
#print(convert_index('ABAD'))

#eeprint(f_support3('III'))

from practice import convert

print(convert('Please do my assiment'))
print(convert('please convert 35 '))
print(convert('Please convert 035 '))
print(convert('Please convert 4000 '))
print(convert('Please convert IIII '))
print(convert('Please convert IXI '))
print(convert('Please convert 35'))
print(convert('Please convert 1982'))
print(convert('Please convert 3007'))
print(convert('Please convert MCMLXXXII'))
print(convert('Please convert MMMVII'))
print(convert('Please convert 123 by using ABC'))
print(convert('Please convert 123 ussing ABC'))
print(convert('Please convert XXXVI using VI'))
print(convert('Please convert XXXVI using IVX'))
print(convert('Please convert XXXVI using XWVI'))
print(convert('Please convert I using II'))
print(convert('Please convert _ using _'))
print(convert('Please convert XXXVI using XVI'))
print(convert('Please convert XXXVI using XABVI'))
print(convert('Please convert EeDEBBBaA using fFeEdDcCbBaA'))
print(convert('Please convert 49036 using fFeEdDcCbBaA'))
print(convert('Please convert 899999999999 using AaBbCcDdEeFfGgHhIiJjKkLl'))
print(convert('Please convert ABCDEFGHIJKLMNOPQRST using AbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStT'))
print(convert('Please convert 1900604 using LAQMPVXYZIRSGN'))
print(convert('Please convert ABCD minimally using ABCDE'))
print(convert('Please convert ABCD minimaly '))
print(convert('Please convert 0I minimaly '))
print(convert('Please convert ABAA minimally '))
print(convert('Please convert ABCDEFA minimally '))
print(convert('Please convert MDCCLXXXVII minimally '))
print(convert('Please convert MDCCLXXXIX minimally '))
print(convert('Please convert MMMVII minimally '))
print(convert('Please convert VI minimally '))
print(convert('Please convert ABCADDEFGF minimally '))
