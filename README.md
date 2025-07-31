# Analisador de Produto para E-commerce 


# O que este projeto faz?

Este programa em Python te ajuda a analisar produtos para sua loja virtual. Ele faz duas coisas principais de forma simples:

1. Compara Preços: Lê os preços de um mesmo produto de diferentes "lojas" (informações que você coloca em um arquivo CSV). Ele calcula o preço médio, o mais barato e o mais caro.
2. Analisa Avaliações: Lê o que as pessoas escreveram sobre o produto ("reviews") e te diz se o sentimento geral é Positivo, Negativo ou Neutro.

Os resultados da análise são mostrados direto no seu Terminal e também são salvos em um arquivo de planilha (`.csv`) para melhor análise.

# Módulos Externos Utilizados

Este projeto usa dois módulos (bibliotecas) Python principais:

* `pandas`: Ajuda a organizar e calcular os dados em tabelas.
* `NLTK` (Natural Language Toolkit): Usado para entender o "sentimento" dos textos das avaliações.