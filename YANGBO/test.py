
from practice import f_support
from practice import perspective
from practice import f_split
from practice import retrospective
from practice import reverse_str




#print(f_split('MDCLXVI'))
#print(f_split('abcdedfhi'))

#print('UNIQUE TEST')
#print(perspective('123','IIV'))


#print('PERSPECTIVE TEST')
print(perspective('XLIX'))
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
t = []
for i in range(1,50):
    a = retrospective(i)
    if len(a) > 3:
        x = a[-4:]

        x = reverse_str(x)
        m = str()
        f = str()
        s = 0 
        for index in x :
           if m != index:
               m = index
               s = s + 1
           f = f + str(s) 
        t.append(f)

        print(a,i,x,m,f)


t.sort()


o = []

for i in t: 
    if i not in o:
        o.append(i) 

print(o)


'''
for i in range(1,4000):
    x = retrospective(i)
    m = perspective(x)

    if i != m:
        print(i,x,m)
'''
