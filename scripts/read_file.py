import json
import mosek

inf = 0

# Função para ler o problema a partir de um arquivo JSON
def read_problem_from_json(file_path):
    with open(file_path, 'r') as file:
        problem = json.load(file)
    return problem

#sense, c, bkx, blx, bux, bkc, blc, buc, asub, aval, vartypeslist

def transform_problem_to_mosek(problem):
    # Define o sentido da função objetivo (maximizar ou minimizar)
    if problem['objective']['sense'] == 'maximize':
        sense = mosek.objsense.maximize
    elif problem['objective']['sense'] == 'minimize':
        sense = mosek.objsense.minimize
    else:
        sense = problem['objective']['sense']

    # Define os coeficientes da função objetivo
    c = problem['objective']['coefficients']

    # Define os limites das variáveis
    bounds = problem['variables']['bounds']
    bkx = []
    blx = []
    bux = []
    for bound in bounds:
        if bound['type'] == 'lo':
            bkx.append(mosek.boundkey.lo)
            blx.append(bound['lower'])
            bux.append(inf)
        elif bound['type'] == 'ra':
            bkx.append(mosek.boundkey.ra)
            blx.append(bound['lower'])
            bux.append(bound['upper'])
        elif bound['type'] == 'up':
            bkx.append(mosek.boundkey.up)
            blx.append(-inf)
            bux.append(bound['value'])
    
    # Define os limites das restrições e a matriz de restrição
    bkc = []
    blc = []
    buc = []
    asub = []
    aval = []
    for constraint in problem['constraints']:
        # Limites
        bound = constraint['bound']
        if bound["type"] == "eq":
            bkc.append(mosek.boundkey.fx)
            blc.append(bound["value"])
            buc.append(bound["value"])
        elif bound["type"] == "le":
            bkc.append(mosek.boundkey.up)
            blc.append(-inf)
            buc.append(bound["value"])
        elif bound["type"] == "ge":
            bkc.append(mosek.boundkey.lo)
            blc.append(bound["value"])
            buc.append(inf)

        # Matriz de restrição
        coef = constraint["coefficients"]
        asub.append([j for j, a in enumerate(coef) if a != 0])
        aval.append([a for a in coef if a != 0])
    
    # Define as variáveis que devem ser inteiras
    if "integer" in problem['variables']:
        vartypes = problem["variables"]["integer"]
    else:
        vartypes = []

    return sense, c, bkx, blx, bux, bkc, blc, buc, asub, aval, vartypes
