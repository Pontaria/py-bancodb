# 🏦 Gerador de dados bancários para teste

Um gerador de dados bancários sintéticos de alta performance construído em Python. Desenvolvido para simular bancos de dados relacionais massivos (milhões de registros) em questão de segundos, aplicando regras de negócio reais do sistema financeiro.

## 🚀 O Projeto

Este script foi criado para popular bancos de dados (MySQL, PostgreSQL, etc.) para testes de carga e aulas de modelagem de dados. Em vez de usar loops tradicionais que tornam a geração lenta, o projeto utiliza **Vetorização com NumPy** e processamento em lote com **Pandas**, permitindo gerar centenas de milhares de transações instantaneamente.

Para a geração de dados "humanos" e realistas (Nomes, CPFs validados, Cartões de Crédito com algoritmo de Luhn), o sistema utiliza a biblioteca **Mimesis**, que é otimizada para velocidade.

## ✨ Features

* **Geração em Cascata:** Respeita a integridade referencial (Agências -> Clientes -> Contas -> Cartões -> Transações).
* **Regras de Negócio Reais:** * Segmentação de clientes (Enterprise, VIP, Regular) com diferentes tetos de saldo e limites de cartão.
  * Transações lógicas (Saques não possuem conta de destino; Depósitos não possuem origem).
  * Prevenção de transferências para a própria conta.
* **Alta Performance:** Substituição de `for loops` por operações vetoriais do `numpy` (`np.where`, arrays booleanos, escolhas randomizadas em bloco).
* **Exportação Flexível:** Suporte para salvar os lotes em `.csv`, `.xlsx` ou `.parquet`.

## 📦 Instalação

Certifique-se de ter o Python 3.8+ instalado. Instale as dependências via pip:

```pip install mimesis numpy pandas```

## 🛠️ Como Usar

- Clone este repositório.

- Execute o script principal:

```python bank-database.py```

- O terminal perguntará o número base de Clientes que você deseja gerar (ex: 100 para testes rápidos ou 300000 para simular um banco real).

- Os arquivos gerados estarão disponíveis na pasta /outputs.

## 🗄️ Estrutura das Entidades Geradas

**Agências:** Distribuídas por tipo (Enterprise, Prime, Regular).

**Clientes:** Nome, CPF, Data de Nascimento, Email, Telefone.

**Contas:** Número formatado (com dígito verificador), Agência, Saldo inicial dinâmico por segmento, Modalidade e Data de Abertura.

**Cartões de Crédito:** Número do cartão validado por bandeira, Validade, Limite (dinâmico) e ID da Conta atrelada.

**Transações:** Tipo (SQ, DP, TR), Valor monetário, Conta Origem, Conta Destino e Timestamp.

## 🧠 Arquitetura e Decisões Técnicas

- O uso de mimesis.payment.credit_card_number() garante que os cartões gerados passem na validação do Algoritmo de Luhn (Módulo 10).

- A lógica de NULL em bancos de dados relacionais foi tratada utilizando o tipo None no Pandas, garantindo uma importação limpa via SQLAlchemy/Bulk Insert posteriormente.

*Desenvolvido para fins educacionais e de demonstração de manipulação massiva de dados em Python.*