with open('var', 'r') as var:
    for v in var:
        with open('nvar', 'w+') as nvar:
            nV = int(v) + 1
            nvar.write(str(nV))

