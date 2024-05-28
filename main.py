import json
import mosek
import sys
import argparse

# Definimos uma constante para o valor de infinito (simbolicamente)
inf = 0.0

# Função para capturar a saída do MOSEK
def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()

# Função para ler o problema a partir de um arquivo JSON
def read_problem_from_json(file_path):
    with open(file_path, 'r') as file:
        problem = json.load(file)
    return problem

# Função para escrever a solução em um arquivo JSON
def write_solution_to_json(input_file, output_file, solution):
    # Lê o problema do arquivo de entrada
    with open(input_file, 'r') as file:
        problem = json.load(file)
    # Adiciona a solução ao problema
    problem['solution'] = solution
    # Escreve o problema atualizado (incluindo a solução) no arquivo de saída
    with open(output_file, 'w') as file:
        json.dump(problem, file, indent=4)

# Função para resolver o problema usando o MOSEK
def solve_problem(problem):
    with mosek.Task() as task:
        # Anexa um log de saída para a tarefa
        task.set_Stream(mosek.streamtype.log, streamprinter)

        # Define o sentido da função objetivo (maximizar ou minimizar)
        obj_sense = mosek.objsense.maximize if problem['objective']['sense'] == 'maximize' else mosek.objsense.minimize
        task.putobjsense(obj_sense)

        # Coeficientes da função objetivo
        c = problem['objective']['coefficients']
        numvar = len(c)

        # Definir limites das variáveis
        bounds = problem['variables']['bounds']
        bkx = []
        blx = []
        bux = []
        for bound in bounds:
            if bound['type'] == 'lo':
                bkx.append(mosek.boundkey.lo)
                blx.append(bound['lower'])
                bux.append(inf if bound['upper'] == 'inf' else bound['upper'])
            elif bound['type'] == 'ra':
                bkx.append(mosek.boundkey.ra)
                blx.append(bound['lower'])
                bux.append(bound['upper'])
            elif bound['type'] == 'fx':
                bkx.append(mosek.boundkey.fx)
                blx.append(bound['value'])
                bux.append(bound['value'])

        # Número de restrições
        numcon = len(problem['constraints'])
        task.appendcons(numcon)
        task.appendvars(numvar)

        # Configurar os limites das variáveis no MOSEK
        for j in range(numvar):
            task.putcj(j, c[j])
            task.putvarbound(j, bkx[j], blx[j], bux[j])
            # Definir tipo de variável como inteiro se especificado
            if 'integer' in problem['variables'] and j in problem['variables']['integer']:
                task.putvartype(j, mosek.variabletype.type_int)
            # Definir tipo de variável como binário se especificado
            if 'binary' in problem['variables'] and j in problem['variables']['binary']:
                task.putvartype(j, mosek.variabletype.type_int)
                task.putvarbound(j, mosek.boundkey.ra, 0, 1)  # Definir limites para variáveis binárias

        # Configurar restrições
        for i, constraint in enumerate(problem['constraints']):
            coef = constraint['coefficients']
            asub = [j for j, a in enumerate(coef) if a != 0]
            aval = [a for a in coef if a != 0]
            bound = constraint['bound']
            if bound['type'] == 'eq':
                task.putconbound(i, mosek.boundkey.fx, bound['value'], bound['value'])
            elif bound['type'] == 'ge':
                task.putconbound(i, mosek.boundkey.lo, bound['value'], inf)
            elif bound['type'] == 'le':
                task.putconbound(i, mosek.boundkey.up, -inf, bound['value'])
            task.putarow(i, asub, aval)

        # Otimiza o problema
        task.optimize()
        task.solutionsummary(mosek.streamtype.msg)

        # Obtém o status da solução
        solsta = task.getsolsta(mosek.soltype.itg if 'integer' in problem['variables'] or 'binary' in problem['variables'] else mosek.soltype.bas)
        if solsta == mosek.solsta.optimal:
            xx = task.getxx(mosek.soltype.itg if 'integer' in problem['variables'] or 'binary' in problem['variables'] else mosek.soltype.bas)
            return {"status": "optimal", "solution": xx.tolist()}
        elif solsta in (mosek.solsta.dual_infeas_cer, mosek.solsta.prim_infeas_cer):
            return {"status": "infeasible"}
        else:
            return {"status": "unknown"}

# Função principal para lidar com argumentos da linha de comando e executar o solver
def main():
    # Analisa os argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Resolve um problema de otimização linear utilizando MOSEK.')
    parser.add_argument('input_file', type=str, help='Caminho para o arquivo JSON com o problema.')
    parser.add_argument('output_file', type=str, help='Caminho para o arquivo JSON onde a solução será salva.')
    args = parser.parse_args()

    try:
        # Lê o problema do arquivo de entrada
        problem = read_problem_from_json(args.input_file)
        # Resolve o problema e obtém a solução
        result = solve_problem(problem)
        if result["status"] == "optimal":
            print("Solução ótima encontrada:")
            for i, val in enumerate(result["solution"]):
                print(f"x[{i}] = {val}")
        else:
            print(f"Status da solução: {result['status']}")
        
        # Escreve a solução no arquivo de saída
        write_solution_to_json(args.input_file, args.output_file, result)
        print(f"Solução escrita em: {args.output_file}")
    except mosek.Error as e:
        # Trata erros específicos do MOSEK
        print("ERRO: %s" % str(e.errno))
        if e.msg is not None:
            print("\t%s" % e.msg)
        sys.exit(1)
    except Exception as e:
        # Trata exceções gerais
        print("Erro:", str(e))
        sys.exit(1)

# Ponto de entrada do script
if __name__ == '__main__':
    main()

