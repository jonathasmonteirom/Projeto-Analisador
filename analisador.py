# --- IMPORTS NECESSÁRIOS ---
import pandas as pd # Usado para trabalhar com tabelas de dados
import nltk # Biblioteca de Processamento de Linguagem Natural
from nltk.sentiment.vader import SentimentIntensityAnalyzer # Ferramenta específica do NLTK para análise de sentimento
import re # Módulo para Expressões Regulares (busca de padrões em texto)
from pathlib import Path # Para trabalhar com caminhos de arquivos de forma simples

# --- FUNÇÃO DE PRÉ-PROCESSAMENTO DE TEXTO ---
def pre_processar_texto(texto: str) -> str:
    """
    Limpa o texto de reviews removendo URLs, menções, hashtags e caracteres não-alfabéticos.
    Isso ajuda a focar nas palavras relevantes para a análise de sentimento.
    """
    if not isinstance(texto, str):
        return ""

    texto = texto.lower()
    texto = re.sub(r'http\S+|www\S+|https\S+', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'@\w+', '', texto)
    texto = re.sub(r'#\w+', '', texto)
    texto = re.sub(r'[^a-zA-ZáàâãéèêíïóôõöúüçÁÀÂÃÉÈÊÍÏÓÔÕÖÚÜÇ\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# --- FUNÇÃO DE ANÁLISE DE SENTIMENTO ---
def analisar_sentimento_do_texto(texto_reviews: str) -> dict:
    """
    Analisa o sentimento de um texto (que pode ser a combinação de várias reviews).
    Retorna um dicionário com a classificação do sentimento (Positivo, Negativo, Neutro)
    e os scores detalhados do NLTK VADER.
    """
    analisador_vader = SentimentIntensityAnalyzer()
    
    # --- TRATAMENTO DE TEXTOS VAZIOS OU NULOS ---
    if not texto_reviews or not texto_reviews.strip():
        return {
            'classificacao_sentimento_geral': 'Neutro (Sem reviews)',
            'score_sentimento_composto': 0.0, 'porcentagem_pos_reviews': 0.0, 'porcentagem_neg_reviews': 0.0, 'porcentagem_neu_reviews': 1.0
        }

    # --- PRÉ-PROCESSAMENTO DO TEXTO PARA ANÁLISE ---
    texto_processado = pre_processar_texto(texto_reviews)
    if not texto_processado.strip(): # Se o texto ficar vazio após a limpeza
        return {
            'classificacao_sentimento_geral': 'Neutro (Após limpeza)',
            'score_sentimento_composto': 0.0, 'porcentagem_pos_reviews': 0.0, 'porcentagem_neg_reviews': 0.0, 'porcentagem_neu_reviews': 1.0
        }

    # --- ANÁLISE COM VADER ---
    scores_vader = analisador_vader.polarity_scores(texto_processado)
    
    # --- CLASSIFICAÇÃO FINAL BASEADA NO SCORE COMPOSTO ---
    score_composto = scores_vader['compound']
    if score_composto >= 0.05:
        classificacao = 'Positivo'
    elif score_composto <= -0.05:
        classificacao = 'Negativo'
    else:
        classificacao = 'Neutro'
    
    return {
        'classificacao_sentimento_geral': classificacao,
        'score_sentimento_composto': score_composto,
        'porcentagem_pos_reviews': scores_vader['pos'],
        'porcentagem_neg_reviews': scores_vader['neg'],
        'porcentagem_neu_reviews': scores_vader['neu']
    }

# --- FUNÇÃO PRINCIPAL DO PROGRAMA ---
def main():
    """
    Função que executa toda a lógica de análise:
    carrega dados, processa, analisa e exibe os resultados.
    """
    print("\n--- Iniciando Analisador de Produto ---")

    # --- 1. CONFIGURAÇÃO DE CAMINHOS DE ARQUIVO ---
    caminho_arquivo_entrada = Path('dados/produtos.csv')
    caminho_arquivo_saida = Path('saida/analise_detalhada.csv')

    # Garante que a pasta 'saida' exista
    caminho_arquivo_saida.parent.mkdir(parents=True, exist_ok=True)

    # --- 2. CARREGAMENTO DOS DADOS ---
    print(f"Carregando dados do arquivo: '{caminho_arquivo_entrada}'...")
    try:
        df_produtos = pd.read_csv(caminho_arquivo_entrada, encoding='utf-8')
        
        if df_produtos.empty:
            print("AVISO: O arquivo de entrada está vazio. Nenhuma análise para realizar.")
            return

        colunas_obrigatorias = ['nome_produto', 'loja', 'preco', 'texto_reviews', 'url_produto']
        if not all(col in df_produtos.columns for col in colunas_obrigatorias):
            print(f"ERRO: O arquivo CSV de entrada deve conter as colunas: {', '.join(colunas_obrigatorias)}")
            print(f"Colunas encontradas: {', '.join(df_produtos.columns)}")
            return

        print(f"Total de {len(df_produtos)} registros de produtos carregados.")

    except FileNotFoundError:
        print(f"ERRO: O arquivo de entrada '{caminho_arquivo_entrada}' não foi encontrado.")
        print("Certifique-se de que o arquivo existe na pasta 'dados/'.")
        return
    except Exception as e:
        print(f"ERRO ao carregar ou ler o arquivo CSV: {e}")
        return

    # --- 3. PRÉ-PROCESSAMENTO DOS PREÇOS ---
    df_produtos['preco'] = pd.to_numeric(df_produtos['preco'], errors='coerce')
    df_produtos.dropna(subset=['preco'], inplace=True) 

    if df_produtos.empty:
        print("AVISO: Nenhum produto com preço válido após a limpeza. Nenhuma análise pode ser feita.")
        return

    # --- 4. ANÁLISE DOS PRODUTOS (Agrupamento Manual e Coleta de Dados) ---
    print("\nRealizando análise de preços e avaliações...")
    
    # Criaremos uma lista de dicionários, onde cada dicionário será uma linha do nosso DataFrame final
    resultados_finais_lista = []

    # Obter a lista de nomes de produtos únicos para iterar sobre eles
    nomes_produtos_unicos = df_produtos['nome_produto'].unique()

    for nome_produto_atual in nomes_produtos_unicos:
        # Filtra o DataFrame para pegar apenas os dados do produto atual
        grupo_do_produto = df_produtos[df_produtos['nome_produto'] == nome_produto_atual]

        # --- Métricas de Preço e Loja ---
        qtd_lojas_encontradas = grupo_do_produto['loja'].nunique()
        preco_minimo = grupo_do_produto['preco'].min()
        preco_maximo = grupo_do_produto['preco'].max()
        preco_medio = grupo_do_produto['preco'].mean()
        
        # Calcula variação de preço percentual, evitando divisão por zero
        variacao_de_preco_percentual = 0.0
        if preco_medio != 0:
            variacao_de_preco_percentual = ((preco_maximo - preco_minimo) / preco_medio) * 100
        
        urls_de_lojas = " | ".join(grupo_do_produto['url_produto'].tolist())

        # --- Análise de Sentimento ---
        # Concatena todos os textos de reviews para este produto
        # .dropna() remove reviews vazias, .astype(str) garante que são strings
        textos_reviews_combinados = " ".join(grupo_do_produto['texto_reviews'].dropna().astype(str))
        
        # Chama a função de análise de sentimento
        resultado_sentimento = analisar_sentimento_do_texto(textos_reviews_combinados)
        
        # --- Adiciona os resultados na lista final ---
        resultados_finais_lista.append({
            'nome_do_produto': nome_produto_atual,
            'qtd_lojas_encontradas': qtd_lojas_encontradas,
            'preco_minimo': preco_minimo,
            'preco_maximo': preco_maximo,
            'preco_medio': preco_medio,
            'variacao_de_preco_percentual': variacao_de_preco_percentual,
            'urls_de_lojas': urls_de_lojas,
            'classificacao_sentimento_geral': resultado_sentimento['classificacao_sentimento_geral'],
            'score_sentimento_composto': resultado_sentimento['score_sentimento_composto'],
            'porcentagem_pos_reviews': resultado_sentimento['porcentagem_pos_reviews'],
            'porcentagem_neg_reviews': resultado_sentimento['porcentagem_neg_reviews'],
            'porcentagem_neu_reviews': resultado_sentimento['porcentagem_neu_reviews']
        })

    # --- 5. Criação do DataFrame Final a partir da Lista ---
    # Convertemos a lista de dicionários em um DataFrame do pandas
    df_analise_completa = pd.DataFrame(resultados_finais_lista)

    if df_analise_completa.empty:
        print("AVISO: Nenhum resultado final gerado. O arquivo de saída não será criado.")
        return

    # --- 6. EXIBIÇÃO DO RESUMO NO TERMINAL ---
    print("\n--- Análise Concluída! Resumo dos Produtos ---")
    
    # Define as colunas que queremos mostrar no resumo do terminal
    colunas_resumo = [
        'nome_do_produto', 
        'preco_medio', 
        'preco_minimo', 
        'preco_maximo', 
        'qtd_lojas_encontradas', 
        'classificacao_sentimento_geral'
    ]
    # Imprime o resumo, arredondando preços e sem mostrar o índice do DataFrame
    # Aqui, df_analise_completa já deve ter todas as colunas corretas.
    print(df_analise_completa[colunas_resumo].round(2).to_string(index=False))

    # --- 7. SALVAMENTO DOS RESULTADOS DETALHADOS EM CSV ---
    try:
        # Salva o DataFrame completo em um arquivo CSV na pasta 'saida'
        df_analise_completa.to_csv(caminho_arquivo_saida, index=False, encoding='utf-8')
        print(f"\nResultados detalhados salvos em: '{caminho_arquivo_saida}'.")
    except Exception as e:
        print(f"ERRO ao salvar os resultados no arquivo CSV: {e}")

# --- CHAMADA PRINCIPAL (para iniciar o programa) ---
# Este bloco garante que o NLTK baixe os dados necessários na primeira execução.
if __name__ == '__main__':
    try:
        # Tenta encontrar o recurso 'vader_lexicon'. Se não encontrar, ele lançará um erro.
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        print("Baixando recurso 'vader_lexicon' do NLTK... (Isso só acontece na primeira execução).")
        # Se não encontrou, faz o download. 'quiet=True' evita imprimir muita coisa se já baixado.
        nltk.download('vader_lexicon', quiet=True)
    
    main() # Chama a função principal para iniciar o programa