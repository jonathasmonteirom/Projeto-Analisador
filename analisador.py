# --- IMPORTS NECESSÁRIOS ---
# Importa o 'pandas', a principal biblioteca para trabalhar com dados em formato de tabela (DataFrames).
# Ele é fundamental para ler o CSV, fazer cálculos e salvar o relatório final.
import pandas as pd 
# Importa o 'nltk', a biblioteca de Processamento de Linguagem Natural (PLN).
import nltk 
# Do 'nltk', importamos o 'SentimentIntensityAnalyzer', a ferramenta que faz a análise de sentimento.
# É a implementação do algoritmo VADER.
from nltk.sentiment.vader import SentimentIntensityAnalyzer 
# Importa o 're', o módulo de expressões regulares, para buscar e manipular padrões em textos.
import re 
# Importa o 'Path' do 'pathlib', que nos ajuda a lidar com caminhos de arquivos de forma segura e moderna.
from pathlib import Path 

# --- FUNÇÃO: pre_processar_texto ---
def pre_processar_texto(texto: str) -> str:
    """
    Esta função prepara o texto das avaliações para a análise.
    Ela realiza uma 'limpeza' para remover informações irrelevantes para o sentimento.
    """
    # Garante que a entrada é uma string válida. Se não for, retorna uma string vazia.
    if not isinstance(texto, str):
        return ""

    # Converte todo o texto para letras minúsculas para padronizar as palavras.
    texto = texto.lower() 
    # Usa 're.sub' para remover URLs (padrões como http://, https://, www.), substituindo-os por nada ('').
    texto = re.sub(r'http\S+|www\S+|https\S+', '', texto) 
    # Remove menções a usuários que começam com '@'.
    texto = re.sub(r'@\w+', '', texto) 
    # Remove hashtags que começam com '#'.
    texto = re.sub(r'#\w+', '', texto) 
    # Remove caracteres que não são letras ou espaços, mantendo acentos.
    texto = re.sub(r'[^a-zA-ZáàâãéèêíïóôõöúüçÁÀÂÃÉÈÊÍÏÓÔÕÖÚÜÇ\s]', '', texto)
    # Substitui múltiplos espaços por um único espaço e remove espaços do início e do final.
    texto = re.sub(r'\s+', ' ', texto).strip() 
    return texto

# --- FUNÇÃO: analisar_sentimento_do_texto ---
def analisar_sentimento_do_texto(texto_reviews: str) -> dict:
    """
    Esta é a parte que realmente 'lê' o sentimento das avaliações.
    O VADER, nossa ferramenta do NLTK, entende se as palavras são positivas ou negativas.
    """
    analisador_vader = SentimentIntensityAnalyzer()
    
    # TRATAMENTO 1: Se o texto original for vazio ou só tiver espaços, retorna "Neutro (Sem reviews)".
    if not texto_reviews or not texto_reviews.strip():
        return {'classificacao_sentimento_geral': 'Neutro (Sem reviews)', 'score_sentimento_composto': 0.0, 'porcentagem_pos_reviews': 0.0, 'porcentagem_neg_reviews': 0.0, 'porcentagem_neu_reviews': 1.0}

    # Pré-processa o texto para limpeza.
    texto_processado = pre_processar_texto(texto_reviews)
    # TRATAMENTO 2: Se, após a limpeza, o texto ficou vazio (ex: era só um link), retorna "Neutro (Após limpeza)".
    if not texto_processado.strip():
        return {'classificacao_sentimento_geral': 'Neutro (Após limpeza)', 'score_sentimento_composto': 0.0, 'porcentagem_pos_reviews': 0.0, 'porcentagem_neg_reviews': 0.0, 'porcentagem_neu_reviews': 1.0}

    # Aplica o modelo VADER para calcular os scores de sentimento do texto limpo.
    scores_vader = analisador_vader.polarity_scores(texto_processado)
    
    score_composto = scores_vader['compound']
    # Com base no score composto (que vai de -1 a +1), classificamos o sentimento geral.
    if score_composto >= 0.05:
        classificacao = 'Positivo'
    elif score_composto <= -0.05:
        classificacao = 'Negativo'
    else:
        classificacao = 'Neutro'
    
    # Retorna um dicionário com o resultado final, que se tornará uma linha na nossa tabela de saída.
    return {
        'classificacao_sentimento_geral': classificacao,
        'score_sentimento_composto': score_composto,
        'porcentagem_pos_reviews': scores_vader['pos'],
        'porcentagem_neg_reviews': scores_vader['neg'],
        'porcentagem_neu_reviews': scores_vader['neu']
    }

# --- FUNÇÃO PRINCIPAL DO PROGRAMA: main() ---
def main():
    """
    Esta é a função que orquestra todo o processo do programa.
    """
    print("\n--- Iniciando Analisador de Produto ---")

    # --- 1. CONFIGURAÇÃO DE CAMINHOS DE ARQUIVO ---
    caminho_arquivo_entrada = Path('dados/produtos.csv')
    caminho_arquivo_saida = Path('saida/analise_detalhada.csv')
    caminho_arquivo_saida.parent.mkdir(parents=True, exist_ok=True) # Garante que a pasta de saída existe.

    # --- 2. CARREGAMENTO E VALIDAÇÃO DOS DADOS ---
    try:
        # Lê os dados do arquivo CSV para um DataFrame (nossa tabela de dados) com o pandas.
        df_produtos = pd.read_csv(caminho_arquivo_entrada, encoding='utf-8')
        if df_produtos.empty:
            print("AVISO: Arquivo de entrada vazio. Nenhuma análise para realizar.")
            return
        print(f"Total de {len(df_produtos)} registros de produtos carregados.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_arquivo_entrada}' não encontrado.")
        return
    except Exception as e:
        print(f"ERRO ao carregar CSV: {e}")
        return

    # --- 3. PRÉ-PROCESSAMENTO DOS PREÇOS ---
    # Transforma a coluna 'preco' em números. Valores inválidos viram 'NaN'.
    df_produtos['preco'] = pd.to_numeric(df_produtos['preco'], errors='coerce')
    # Remove as linhas onde o preço não é válido.
    df_produtos.dropna(subset=['preco'], inplace=True) 
    if df_produtos.empty:
        print("AVISO: Nenhum produto com preço válido para análise.")
        return

    # --- 4. ANÁLISE E AGRUPAMENTO DOS PRODUTOS ---
    print("\nRealizando análise de preços e avaliações...")
    
    resultados_finais_lista = []
    # Itera sobre cada nome de produto único para consolidar os dados de todas as lojas.
    for nome_produto_atual in df_produtos['nome_produto'].unique():
        # Filtra o DataFrame para pegar apenas os dados do produto que estamos analisando agora.
        grupo_do_produto = df_produtos[df_produtos['nome_produto'] == nome_produto_atual]

        # --- Cálculos de Preço e Análise de Sentimento ---
        # Pega o menor, maior e médio preço do grupo.
        preco_minimo = grupo_do_produto['preco'].min()
        preco_maximo = grupo_do_produto['preco'].max()
        preco_medio = grupo_do_produto['preco'].mean()
        # Conta quantas lojas únicas existem no grupo.
        qtd_lojas_encontradas = grupo_do_produto['loja'].nunique()
        # Junta todas as URLs em uma única string.
        urls_de_lojas = " | ".join(grupo_do_produto['url_produto'].tolist())

        # Concatena todas as reviews do produto em uma única string.
        textos_reviews_combinados = " ".join(grupo_do_produto['texto_reviews'].dropna().astype(str))
        # Chama a função que faz a análise de sentimento com o texto combinado.
        resultado_sentimento = analisar_sentimento_do_texto(textos_reviews_combinados)
        
        # --- Armazena resultados na lista ---
        # Cria um dicionário com todos os resultados para este produto.
        resultados_finais_lista.append({
            'nome_do_produto': nome_produto_atual,
            'qtd_lojas_encontradas': qtd_lojas_encontradas,
            'preco_minimo': preco_minimo,
            'preco_maximo': preco_maximo,
            'preco_medio': preco_medio,
            'classificacao_sentimento_geral': resultado_sentimento['classificacao_sentimento_geral'],
            'urls_de_lojas': urls_de_lojas,
        })

    # --- 5. CRIAÇÃO E EXIBIÇÃO DO RELATÓRIO FINAL ---
    # Transforma a lista de dicionários em um DataFrame para ter a tabela de resultados.
    df_analise_completa = pd.DataFrame(resultados_finais_lista)
    if df_analise_completa.empty:
        print("AVISO: Nenhum resultado final gerado.")
        return

    print("\n--- Análise Concluída! Resumo dos Produtos ---")
    # Colunas que serão mostradas no resumo do Terminal.
    colunas_resumo = ['nome_do_produto', 'preco_medio', 'preco_minimo', 'preco_maximo', 
                      'qtd_lojas_encontradas', 'classificacao_sentimento_geral']
    # Imprime a tabela de resumo. '.round(2)' arredonda os números. '.to_string(index=False)' remove a coluna de índice.
    print(df_analise_completa[colunas_resumo].round(2).to_string(index=False))

    # --- 6. SALVAMENTO DOS RESULTADOS ---
    try:
        # Salva o DataFrame completo em um arquivo CSV.
        df_analise_completa.to_csv(caminho_arquivo_saida, index=False, encoding='utf-8')
        print(f"\nResultados detalhados salvos em: '{caminho_arquivo_saida}'.")
    except Exception as e:
        print(f"ERRO ao salvar os resultados no CSV: {e}")

# --- CHAMADA PRINCIPAL ---
# Este bloco garante que o programa comece a execução e que o NLTK esteja pronto.
if __name__ == '__main__':
    # Verifica se os dados necessários para o NLTK estão baixados. Se não estiverem, ele os baixa.
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        print("Baixando recurso 'vader_lexicon' do NLTK... (Isso só acontece na primeira execução).")
        nltk.download('vader_lexicon', quiet=True)
    
    main()