# Analisador de Produtos

Este é um programa em Python que criado para ajudar a escolher produtos pra vender. A ideia é simples: ele lê dados de produtos que você coloca num arquivo e faz um resumo pra você.

O que ele faz?

1.  **Compara Preços:** Pega o preço do mesmo produto em várias lojas e te diz qual é o mais barato, o mais caro e a média.
2.  **Lê as Avaliações:** Analisa o que os clientes estão dizendo sobre o produto e te diz se a galera curtiu (Positivo), não gostou (Negativo) ou se tá tudo na média (Neutro).

No final, ele mostra um resumo no Terminal e salva tudo numa planilha.

---

# Como Usar

**1. Preparando:**

* Você precisa ter o **Python** no seu PC.
* Crie a pasta `analisador_ecommerce` e as subpastas `dados` e `saida` dentro dela.
* Crie os arquivos `analisador.py`, `README.md` e `requirements.txt` na pasta principal.
* Crie o arquivo `produtos.csv` na pasta `dados`.

**2. Colocar seus dados:**

* Abra o arquivo `produtos.csv` e coloque as informações dos produtos que você quer analisar. Lembrar de seguir o formato `nome_produto,loja,preco,texto_reviews,url_produto`.
* É importante que o **`nome_produto` seja idêntico** para o mesmo item em lojas diferentes!
* Se não tiver review, deixe o campo `texto_reviews` em branco.

**3. Rodar:**

* Abra o Terminal na pasta do projeto.
* Ative o ambiente virtual (`.\venv\Scripts\activate` ou `source venv/bin/activate`).
* Instale o que o programa precisa: `pip install -r requirements.txt`.
* Execute o programa: `python analisador.py`.

Agora é só olhar a saída no Terminal ou abrir o arquivo `analise_detalhada.csv` na pasta `saida` pra ver o relatório completo.

---

# Ferramentas Usadas

* **`pandas`**: Pra organizar os dados em tabelas (o Excel do Python).
* **`NLTK`**: Pra fazer a análise de texto e de sentimento.