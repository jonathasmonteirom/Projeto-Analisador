# --- IMPORTS NECESSÁRIOS
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from pathlib import Path

# --- FUNÇÃO: Pré-processamento de Texto
def pre_processar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = re.sub(r'http\S+|www\S+|https\S+', '', texto)
    texto = re.sub(r'@\w+', '', texto)
    texto = re.sub(r'#\w+', '', texto)
    texto = re.sub(r'[^a-zA-ZáàâãéèêíïóôõöúüçÁÀÂÃÉÈÊÍÏÓÔÕÖÚÜÇ\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# --- FUNÇÃO: Análise de Sentimento
def analisar_sentimento_do_texto(texto_reviews: str) -> dict:
    analisador_vader = SentimentIntensityAnalyzer()
    
    if not texto_reviews or not texto_reviews.strip():
        return {'classificacao_sentimento_geral': 'Neutro (Sem reviews)', 'score_sentimento_composto': 0.0, 
                'porcentagem_pos_reviews': 0.0, 'porcentagem_neg_reviews': 0.0, 'porcentagem_neu_reviews': 1.0}

    texto_processado = pre_processar_texto(texto_reviews)
    if not texto_processado.strip():
        return {'classificacao_sentimento_geral': 'Neutro (Após limpeza)', 'score_sentimento_composto': 0.0, 
                'porcentagem_pos_reviews': 0.0, 'porcentagem_neg_reviews': 0.0, 'porcentagem_neu_reviews': 1.0}

    scores_vader = analisador_vader.polarity_scores(texto_processado)
    
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

# --- FUNÇÃO PRINCIPAL DO PROGRAMA
def main():
    print("\n--- Iniciando Analisador de Produto ---")

    # --- Configuração de Caminhos
    caminho_arquivo_entrada = Path('dados/produtos.csv')
    caminho_arquivo_saida = Path('saida/analise_detalhada.csv')
    caminho_arquivo_saida.parent.mkdir(parents=True, exist_ok=True)

    # --- Carregamento e Validação dos Dados
    try:
        df_produtos = pd.read_csv(caminho_arquivo_entrada, encoding='utf-8')
        if df_produtos.empty:
            print("AVISO: Arquivo de entrada vazio. Nenhuma análise para realizar.")
            return

        colunas_obrigatorias = ['nome_produto', 'loja', 'preco', 'texto_reviews', 'url_produto']
        if not all(col in df_produtos.columns for col in colunas_obrigatorias):
            print(f"ERRO: CSV deve conter: {', '.join(colunas_obrigatorias)}. Encontradas: {', '.join(df_produtos.columns)}")
            return
        print(f"Total de {len(df_produtos)} registros de produtos carregados.")

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_arquivo_entrada}' não encontrado.")
        return
    except Exception as e:
        print(f"ERRO ao carregar CSV: {e}")
        return

    # --- Pré-processamento de Preços
    df_produtos['preco'] = pd.to_numeric(df_produtos['preco'], errors='coerce')
    df_produtos.dropna(subset=['preco'], inplace=True) 
    if df_produtos.empty:
        print("AVISO: Nenhum produto com preço válido após limpeza. Análise abortada.")
        return

    # --- Análise por Produto e Agrupamento
    print("\nRealizando análise de preços e avaliações...")
    
    resultados_finais_lista = []
    for nome_produto_atual in df_produtos['nome_produto'].unique():
        grupo_do_produto = df_produtos[df_produtos['nome_produto'] == nome_produto_atual]

        # Métricas de Preço e Loja
        qtd_lojas_encontradas = grupo_do_produto['loja'].nunique()
        preco_minimo = grupo_do_produto['preco'].min()
        preco_maximo = grupo_do_produto['preco'].max()
        preco_medio = grupo_do_produto['preco'].mean()
        variacao_de_preco_percentual = ((preco_maximo - preco_minimo) / preco_medio) * 100 if preco_medio != 0 else 0.0
        urls_de_lojas = " | ".join(grupo_do_produto['url_produto'].tolist())

        # Análise de Sentimento
        textos_reviews_combinados = " ".join(grupo_do_produto['texto_reviews'].dropna().astype(str))
        resultado_sentimento = analisar_sentimento_do_texto(textos_reviews_combinados)
        
        # Adiciona os resultados na lista final
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

    # --- Criação e Exibição do DataFrame Final
    df_analise_completa = pd.DataFrame(resultados_finais_lista)
    if df_analise_completa.empty:
        print("AVISO: Nenhum resultado final gerado.")
        return

    print("\n--- Análise Concluída! Resumo dos Produtos ---")
    colunas_resumo = [
        'nome_do_produto', 'preco_medio', 'preco_minimo', 'preco_maximo', 
        'qtd_lojas_encontradas', 'classificacao_sentimento_geral'
    ]
    print(df_analise_completa[colunas_resumo].round(2).to_string(index=False))

    # --- Salvamento dos Resultados Detalhados
    try:
        df_analise_completa.to_csv(caminho_arquivo_saida, index=False, encoding='utf-8')
        print(f"\nResultados detalhados salvos em: '{caminho_arquivo_saida}'.")
    except Exception as e:
        print(f"ERRO ao salvar os resultados no CSV: {e}")

# --- Chamada Principal (garante NLTK download na primeira vez)
if __name__ == '__main__':
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        print("Baixando recurso 'vader_lexicon' do NLTK... (Isso só acontece na primeira execução).")
        nltk.download('vader_lexicon', quiet=True)
    
    main()