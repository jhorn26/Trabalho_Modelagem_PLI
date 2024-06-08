import sys
import argparse
import mosek
import json

from scripts.read_file import read_problem_from_json, transform_problem_to_mosek
from scripts.solve_problem_mosek import solve_problem_continuos, solve_problem_integer

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
        # Encontra as variáveis para resolver o problema
        sense, c, bkx, blx, bux, bkc, blc, buc, asub, aval, vartypes = transform_problem_to_mosek(problem)
        # Resolve o problema e obtém a solução
        if vartypes:
            result = solve_problem_integer(sense, c, bkx, blx, bux, bkc, blc, buc, asub, aval, vartypes)
        else:
            result = solve_problem_continuos(sense, c, bkx, blx, bux, bkc, blc, buc, asub, aval)
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

