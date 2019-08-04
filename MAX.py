





def summa_chisel(pervoe, vtoroe):
    return pervoe + vtoroe

def umnozenie(pervoe, vtoroe):
    return pervoe * vtoroe

def kvadrat(chislo):
    return chislo * chislo


x = summa_chisel(500, 200)

if x > 300:
    x = x/100
else:
    print('Nihua')


y = umnozenie(25, x)

z = kvadrat(y)




print('SUMMA', x)
print('Umnozenie', y)
print('Kvadrat', z)



