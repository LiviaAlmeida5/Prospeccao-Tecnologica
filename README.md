# Prospecção-Tecnológica

# POC - Comparação MongoDB vs Neo4j vs Cassandra

Este projeto é uma Prova de Conceito (POC) para comparar diferentes bancos de dados NoSQL utilizando um cenário de rede social.

A aplicação utiliza:

- **MongoDB** para armazenamento de usuários em documentos;
- **Neo4j** para representar relacionamentos entre usuários utilizando grafos;
- **Cassandra** para armazenamento de publicações.

Também é realizado um benchmark comparando o desempenho de consultas de relacionamentos entre **MongoDB** e **Neo4j**.

---

# Tecnologias utilizadas

- Python 3
- Docker
- Docker Compose
- MongoDB
- Neo4j
- Apache Cassandra

Bibliotecas Python utilizadas:

- pymongo
- neo4j
- cassandra-driver

---

# Estrutura do projeto

```
.
├── docker-compose.yml
├── scripts
│   ├── CassandraNeo4jMongo.py
│   └── ComparaçãoMongoNeo4j.py
└── README.md
```

Descrição dos arquivos:

## CassandraNeo4jMongo.py

Arquivo responsável pelo exemplo básico de utilização dos bancos.

Realiza:

- criação de usuários no MongoDB;
- criação de relacionamentos no Neo4j;
- criação de posts no Cassandra.

---

## ComparaçãoMongoNeo4j.py

Arquivo responsável pelo teste de desempenho.

Realiza:

- limpeza das bases;
- criação de usuários de teste;
- geração de relacionamentos;
- execução de consultas no MongoDB;
- execução de consultas no Neo4j;
- comparação dos tempos de execução.

---

# Pré-requisitos

Instale:

## Docker

Verifique:

```bash
docker --version
```

## Docker Compose

Verifique:

```bash
docker compose version
```

## Python

Verifique:

```bash
python3 --version
```

---

# Inicializando os bancos

Na raiz do projeto execute:

```bash
docker compose up -d
```

Serão iniciados:

| Banco | Porta |
|---|---|
| MongoDB | 27017 |
| Neo4j Browser | 7474 |
| Neo4j Bolt | 7687 |
| Cassandra | 9042 |

Verifique os containers:

```bash
docker ps
```

Saída esperada:

```
mongodb
neo4j
cassandra
```

---

# Configurando ambiente Python

Crie um ambiente virtual:

```bash
python3 -m venv venv
```

Ative:

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Instale as dependências:

```bash
pip install pymongo neo4j cassandra-driver
```

---

# Executando o exemplo básico

Com os containers ativos execute:

```bash
python scripts/CassandraNeo4jMongo.py
```

O programa irá criar:

## MongoDB

Usuários:

```json
{
    "nome": "Ana"
}
```

---

## Neo4j

Relacionamento:

```
(João)-[:SEGUE]->(Ana)
```

---

## Cassandra

Post:

```
Usuário: Ana

Conteúdo:
Olá, esse é meu primeiro post!
```

---

# Executando o benchmark

Para executar a comparação entre MongoDB e Neo4j:

```bash
python scripts/ComparaçãoMongoNeo4j.py
```

O benchmark utiliza:

```python
NUM_USUARIOS = 1000
SEGUIDOS_POR_USUARIO = 10
PROFUNDIDADE = 4
REPETICOES = 10
```

Configuração:

- 1000 usuários;
- cada usuário segue 10 pessoas;
- busca de relacionamentos até profundidade 4;
- 10 execuções para calcular a média.

---

# Funcionamento do Benchmark

## MongoDB

Os relacionamentos são armazenados em documentos:

Exemplo:

```json
{
    "nome": "Usuario0",
    "segue": [
        "Usuario1",
        "Usuario2"
    ]
}
```

A busca é feita percorrendo os documentos usando Python.

---

## Neo4j

Os usuários são armazenados como nós:

```
(User)
```

E os relacionamentos:

```
(User)-[:SEGUE]->(User)
```

A consulta é feita utilizando Cypher:

```cypher
MATCH (u:User)
      -[:SEGUE*1..4]->
      (destino)

RETURN count(DISTINCT destino)
```

---

# Resultado esperado

Ao finalizar o benchmark será exibido:

```
==============================
RESULTADO FINAL
==============================

MongoDB média : XX ms
Neo4j média   : XX ms
```

Também será informado qual banco apresentou melhor desempenho.

---

# Parando os serviços

Para desligar os containers:

```bash
docker compose down
```

---

# Removendo os dados

Para apagar também os volumes:

```bash
docker compose down -v
```

Isso remove:

- dados do MongoDB;
- dados do Neo4j;
- dados do Cassandra.

---

# Objetivo

Esta POC demonstra diferenças entre três modelos NoSQL:

## MongoDB

Modelo:

```
Documento
```

Utilizado para:

- documentos JSON;
- dados flexíveis;
- consultas por registro.

---

## Neo4j

Modelo:

```
Grafo
```

Utilizado para:

- redes sociais;
- recomendações;
- consultas envolvendo relacionamentos.

---

## Cassandra

Modelo:

```
Colunar distribuído
```

Utilizado para:

- grande volume de dados;
- alta disponibilidade;
- escrita rápida.

---
