from practice import f_support
from practice import perspective
from practice import f_split

a,b,c = f_support('IV','XVI')
print(a,b,c)


a,b,c = f_support('IIV','XVI')
print(a,b,c)

a,b,c = f_support('IX','XVI')
print(a,b,c)



print(f_split('MDCLXVI'))
print(f_split('abcdedfhi'))

print('UNIQUE TEST')
print(perspective('123','IIV'))


print('PERSPECTIVE TEST')

print(perspective('XVII'))
print(perspective('MCMLXXXII'))
print(perspective(grn='M',grs='MDCLXVI'))
print(perspective(grn='EeDEBBBaA',grs='fFeEdDcCbBaA'))
print(perspective(grn='ABCDEFGHIJKLMNOPQRST',grs='AbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStT'))
print(perspective(grn='IIII'))
print(perspective(grn='AMAZING',grs='LAQMPVXYZIRSGN'))
print(perspective('VI'))
