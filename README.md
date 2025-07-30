# Analisador de Produto para E-commerce (Versão Simples com CSV Externo)

## O que este projeto faz?

Este programa em Python te ajuda a analisar produtos para sua loja virtual. Ele faz duas coisas principais de forma simples:

1.  **Compara Preços:** Lê os preços de um mesmo produto de diferentes "lojas" (informações que você coloca em um arquivo CSV). Ele calcula o preço médio, o mais barato e o mais caro.
2.  **Analisa Avaliações:** Lê o que as pessoas escreveram sobre o produto ("reviews") e te diz se o sentimento geral é Positivo, Negativo ou Neutro.

Os resultados da análise são mostrados direto no seu Terminal e também são salvos em um arquivo de planilha (`.csv`) para você analisar melhor.

## 2. Módulos Externos Utilizados

Este projeto usa dois módulos (bibliotecas) Python principais:

* **`pandas`**: Ajuda a organizar e calcular os dados em tabelas.
* **`NLTK` (Natural Language Toolkit)**: Usado para entender o "sentimento" dos textos das avaliações.

## 3. Como usar (Passo a Passo)

### 3.1. Preparação Inicial

* **Tenha Python 3.6 ou mais novo instalado.**
* **Crie as Pastas:**
    * Abra o Terminal (ou Prompt de Comando no Windows).
    * Vá para o lugar onde quer criar o projeto (ex: `cd ~/Documentos` ou `cd C:\Users\SeuUsuario\Documentos`).
    * Crie a pasta principal: `mkdir analisador_produto_simples_csv`
    * Entre nela: `cd analisador_produto_simples_csv`
    * Crie as subpastas: `mkdir dados` e `mkdir saida`
* **Crie os Arquivos:**
    * Crie os arquivos vazios: `analisador.py`, `README.md`, `requirements.txt` na pasta principal.
    * Crie o arquivo `produtos.csv` dentro da pasta `dados/`.
* **Cole o Conteúdo:**
    * Copie o código completo do `analisador.py` (desta resposta) e cole no seu arquivo `analisador.py`.
    * Copie o conteúdo do `dados/produtos.csv` (desta resposta) e cole no seu arquivo `dados/produtos.csv`. **Este é o arquivo que você vai editar com os dados dos SEUS produtos.**
    * Copie o conteúdo do `requirements.txt` (desta resposta) e cole no seu arquivo `requirements.txt`.
    * **SALVE TODOS OS ARQUIVOS!**

### 3.2. Configuração do Ambiente (Uma Única Vez)

* **Abra o Terminal** e vá para a pasta `analisador_produto_simples_csv/`.
* **Crie e Ative um "Ambiente Virtual"**:
    * **Criar:** `python -m venv venv`
    * **Ativar:**
        * **No Windows (Prompt de Comando):** `.\venv\Scripts\activate.bat`
        * **No Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
            * *Se der erro de "execução de scripts desabilitada", você precisa rodar o comando `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` em um PowerShell **como Administrador**, confirmar, fechar o PowerShell de Administrador e tentar ativar o ambiente virtual novamente em um PowerShell **NORMAL**.*
        * **No macOS/Linux:** `source venv/bin/activate`
    * Você verá `(venv)` no começo da linha do Terminal, indicando que o ambiente está ativo.
* **Instale o que o programa precisa:**
    * Com `(venv)` ativo, execute:
        ```bash
        pip install -r requirements.txt
        ```
* **Baixe um dado extra para análise de texto (NLTK):**
    * Com `(venv)` ativo, digite `python` e Enter.
    * ```python
        import nltk
        nltk.download('vader_lexicon')
        exit()
        ```

### 3.3. Rodar o Programa

* **Abra o Terminal** (com `(venv)` ativo e na pasta `analisador_produto_simples_csv/`).
* **Execute:**
    ```bash
    python analisador.py
    ```

### 3.4. Onde ver os resultados

* Você verá um resumo da análise no próprio Terminal.
* Um arquivo chamado `analise_detalhada.csv` será criado dentro da pasta `saida/` com todos os resultados completos. Você pode abrir este arquivo com Excel, Google Sheets ou outro programa de planilhas.

## 4. Como usar com SEUS produtos

1.  **Abra o arquivo `dados/produtos.csv`** (usando Excel, Google Sheets ou um editor de texto).
2.  **Edite ou adicione linhas com os dados dos SEUS produtos.**
    * Siga o formato das colunas: `nome_produto,loja,preco,texto_reviews,url_produto`
    * **Importante:** Para que o programa agrupe as informações de um **MESMO produto** (mas de lojas diferentes), o `nome_produto` deve ser **EXATAMENTE IGUAL** em todas as linhas que se referem a ele.
    * **Se não tiver reviews:** Deixe a célula da coluna `texto_reviews` **em branco** no CSV.
3.  **Salve o `produtos.csv`** depois de fazer suas alterações.
4.  **Execute o programa novamente:** `python analisador.py`

## 5. Próximas Ideias (Melhorias Futuras)

* **Web Scraping:** Fazer o programa ir direto nas lojas online para coletar os dados, em vez de você ter que preencher o CSV. Isso é mais avançado!
* **Gráficos Simples:** Adicionar a criação de gráficos visuais dos resultados.
* **Mais Detalhes:** Extrair outras informações como descrição do produto ou categoria.