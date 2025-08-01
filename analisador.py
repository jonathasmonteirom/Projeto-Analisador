# --- IMPORTS NECESSÁRIOS ---
# Importa o 'pandas', a principal biblioteca para trabalhar com dados em formato de tabela (DataFrames).
# No projeto, o pandas é o que permite ler o CSV, fazer cálculos e salvar o relatório.
import pandas as pd 
# Importa o 'nltk', que é uma biblioteca para entender e processar textos.
import nltk 
# Do 'nltk', importamos o 'SentimentIntensityAnalyzer', a ferramenta que faz a análise de sentimento.
from nltk.sentiment.vader import SentimentIntensityAnalyzer 
# Importa o 're' para usar expressões regulares, que ajuda a encontrar e substituir padrões em textos.
import re 
# Importa o 'Path' do 'pathlib', que é um jeito mais moderno e seguro de lidar com caminhos de arquivos.
from pathlib import Path 

# --- FUNÇÃO: pre_processar_texto ---
def pre_processar_texto(texto: str) -> str:
    """
    Esta função prepara o texto das avaliações para a análise.
    É como uma "limpeza" que remove coisas que não são relevantes para o sentimento.
    """
    if not isinstance(texto, str):
        return "" # Garante que só seja processado textos válidos.

    texto = texto.lower() # Converte tudo para minúsculas para padronizar as palavras.
    texto = re.sub(r'http\S+|www\S+|https\S+', '', texto) # Remove URLs, que não têm sentimento.
    texto = re.sub(r'@\w+', '', texto) # Remove menções, que também não têm sentimento.
    texto = re.sub(r'#\w+', '', texto) # Remove hashtags.
    texto = re.sub(r'[^a-zA-ZáàâãéèêíïóôõöúüçÁÀÂÃÉÈÊÍÏÓÔÕÖÚÜÇ\s]', '', texto) # Remove números e símbolos, mantendo apenas letras e acentos.
    texto = re.sub(r'\s+', ' ', texto).strip() # Deixa apenas um espaço entre as palavras e remove espaços extras das pontas.
    return texto

# --- FUNÇÃO: analisar_sentimento_do_texto ---
def analisar_sentimento_do_texto(texto_reviews: str) -> dict:
    """
    Esta é a parte que realmente "lê" o sentimento das avaliações.
    O VADER, nossa ferramenta do NLTK, entende se as palavras são positivas ou negativas.
    """
    analisador_vader = SentimentIntensityAnalyzer()
    
    # Este é um tratamento para casos em que o texto de review está vazio.
    # O programa retorna um resultado "Neutro" com scores zerados para não dar erro.
    if not texto_reviews or not texto_reviews.strip():
        return {'classificacao_sentimento_geral': 'Neutro (Sem reviews)', 'score_sentimento_composto': 0.0, 'porcentagem_pos_reviews': 0.0, 'porcentagem_neg_reviews': 0.0, 'porcentagem_neu_reviews': 1.0}

    texto_processado = pre_processar_texto(texto_reviews)
    # Se, depois da limpeza, o texto ficou vazio (ex: a review era só um link),
    # o programa também classifica como neutro para não processar nada.
    if not texto_processado.strip():
        return {'classificacao_sentimento_geral': 'Neutro (Após limpeza)', 'score_sentimento_composto': 0.0, 'porcentagem_pos_reviews': 0.0, 'porcentagem_neg_reviews': 0.0, 'porcentagem_neu_reviews': 1.0}

    # Aqui o VADER calcula os scores de sentimento (neg, pos, neu) para o texto.
    scores_vader = analisador_vader.polarity_scores(texto_processado)
    
    score_composto = scores_vader['compound']
    # Com base no score composto (que vai de -1 a +1), é classificado o sentimento.
    if score_composto >= 0.05:
        classificacao = 'Positivo'
    elif score_composto <= -0.05:
        classificacao = 'Negativo'
    else:
        classificacao = 'Neutro'
    
    # Retorna um dicionário com o resultado final, que se tornará uma linha na tabela de saída.
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
    Esta é a função que orquestra todo o processo.
    É aqui que o programa começa, carrega os dados e chama as outras funções.
    """
    print("\n--- Iniciando Analisador de Produto ---")

    # --- CARREGAMENTO E VALIDAÇÃO DOS DADOS ---
    caminho_arquivo_entrada = Path('dados/produtos.csv')
    caminho_arquivo_saida = Path('saida/analise_detalhada.csv')
    caminho_arquivo_saida.parent.mkdir(parents=True, exist_ok=True) # Garante que a pasta 'saida' existe.

    try:
        # Lê os dados do arquivo CSV para um DataFrame (tabela de dados) com o pandas.
        df_produtos = pd.read_csv(caminho_arquivo_entrada, encoding='utf-8')
        if df_produtos.empty:
            print("AVISO: Arquivo de entrada vazio.")
            return

        print(f"Total de {len(df_produtos)} registros de produtos carregados.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_arquivo_entrada}' não encontrado.")
        return
    except Exception as e:
        print(f"ERRO ao carregar CSV: {e}")
        return

    # --- PRÉ-PROCESSAMENTO DOS PREÇOS ---
    # Transforma a coluna 'preco' em números. Se o valor for inválido, ele vira um 'NaN'.
    df_produtos['preco'] = pd.to_numeric(df_produtos['preco'], errors='coerce')
    df_produtos.dropna(subset=['preco'], inplace=True) # Remove as linhas onde o preço não é válido.
    if df_produtos.empty:
        print("AVISO: Nenhum produto com preço válido para análise.")
        return

    # --- ANÁLISE E AGRUPAMENTO DOS PRODUTOS ---
    print("\nRealizando análise de preços e avaliações...")
    
    resultados_finais_lista = []
    # Itera sobre cada produto único para consolidar os dados de todas as lojas.
    for nome_produto_atual in df_produtos['nome_produto'].unique():
        # Filtra o DataFrame para pegar apenas os dados do produto que está sendo analisado.
        grupo_do_produto = df_produtos[df_produtos['nome_produto'] == nome_produto_atual]

        # --- Cálculos de Preço e Análise de Sentimento ---
        preco_minimo = grupo_do_produto['preco'].min()
        preco_maximo = grupo_do_produto['preco'].max()
        preco_medio = grupo_do_produto['preco'].mean()
        qtd_lojas_encontradas = grupo_do_produto['loja'].nunique()
        urls_de_lojas = " | ".join(grupo_do_produto['url_produto'].tolist())

        # Concatena todas as reviews do produto em uma única string.
        textos_reviews_combinados = " ".join(grupo_do_produto['texto_reviews'].dropna().astype(str))
        # Chama a função que faz a análise de sentimento.
        resultado_sentimento = analisar_sentimento_do_texto(textos_reviews_combinados)
        
        # --- Armazena os resultados na lista ---
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

    # --- CRIAÇÃO E EXIBIÇÃO DO RELATÓRIO FINAL ---
    df_analise_completa = pd.DataFrame(resultados_finais_lista)
    if df_analise_completa.empty:
        print("AVISO: Nenhum resultado final gerado.")
        return

    print("\n--- Análise Concluída! Resumo dos Produtos ---")
    colunas_resumo = ['nome_do_produto', 'preco_medio', 'preco_minimo', 'preco_maximo', 
                      'qtd_lojas_encontradas', 'classificacao_sentimento_geral']
    print(df_analise_completa[colunas_resumo].round(2).to_string(index=False))

    # --- SALVAMENTO DOS RESULTADOS ---
    try:
        df_analise_completa.to_csv(caminho_arquivo_saida, index=False, encoding='utf-8')
        print(f"\nResultados detalhados salvos em: '{caminho_arquivo_saida}'.")
    except Exception as e:
        print(f"ERRO ao salvar os resultados no CSV: {e}")

# --- CHAMADA PRINCIPAL ---
# Este bloco garante que o programa comece a execução e que o NLTK esteja pronto.
if __name__ == '__main__':
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        print("Baixando recurso 'vader_lexicon' do NLTK... (Isso só acontece na primeira execução).")
        nltk.download('vader_lexicon', quiet=True)
    
    main()