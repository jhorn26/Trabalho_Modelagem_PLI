<h1 align="center">Programação Linear e Inteira

Trabalho de Modelagem</h1>

## Descrição do Projeto

Este repositório contém a Avaliação 2 da disciplina de Programação Linear e Inteira (PLI) da FGV EMAp - 2024.1. O objetivo do trabalho é resolver problemas de modelagem utilizando técnicas de PLI.

## Estrutura do Repositório

- `exemplos/`: Exemplos da utilização do código.
- `exercicios e gabarito/`: Exercícios a serem resolvidos, com suas respectivas modelagens na linguagem de PLI.
- `problemas/`: Contém os exercícios modelados, no formato JSON, que serão usados no código.
- `scripts/`: Contém funções auxiliares para a main.py.
- `solucoes/`: Contém os resultados gerados.

## Instruções de Execução

1. **Clonar o repositório:**
    ```sh
    git clone https://github.com/jhorn26/Trabalho_Modelagem_PLI.git
    cd Trabalho_Modelagem_PLI
    ```

2. **Instalar as dependências:**
    Recomendamos o uso de um ambiente virtual para gerenciar as dependências do projeto. Para criar e ativar um ambiente virtual, execute:
    ```sh
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
3. **Executar os scripts:**
    A `main.py` necessita de dois argumentos, `.json` com o caminho do problema e o caminho para solução, também em `.json`. Por exemplo:
    ```sh
    python main.py problemas/exercicio.json solucoes/solucao_exercicio.json
    ```
    
## Autores

- <a href="https://github.com/Daniel-Falqueto" target="_blank"> Daniel Ambrosin Falqueto
- <a href="https://github.com/jhorn26" target="_blank"> Jean Fernando Horn
- <a href="https://github.com/pabl0ck" target="_blank"> Pablo Andrade Carvalho Barros

## Agradecimentos especiais

- Professor <a href="https://www.vincentgyg.com/" target="_blank">Vincent Guigues</a>
