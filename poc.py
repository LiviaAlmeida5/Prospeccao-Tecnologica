from pymongo import MongoClient
from neo4j import GraphDatabase
from cassandra.cluster import Cluster
from datetime import datetime

# ---------------- MongoDB (Usuários) ----------------
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["poc"]
usuarios = mongo_db["usuarios"]

def criar_usuario(nome):
    user = {"nome": nome}
    result = usuarios.insert_one(user)
    print(f"Usuário criado no MongoDB: {nome}")
    return str(result.inserted_id)

# ---------------- Neo4j (Relacionamentos) ----------------
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "senha123"))

def seguir(usuario1, usuario2):
    with neo4j_driver.session() as session:
        session.run(
            "MERGE (a:User {nome: $u1}) "
            "MERGE (b:User {nome: $u2}) "
            "MERGE (a)-[:SEGUE]->(b)",
            u1=usuario1, u2=usuario2
        )
    print(f"{usuario1} agora segue {usuario2} no Neo4j")

# ---------------- Cassandra (Posts) ----------------
cluster = Cluster(["127.0.0.1"])
session = cluster.connect()

session.execute("""
CREATE KEYSPACE IF NOT EXISTS poc
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
""")

session.set_keyspace("poc")

session.execute("""
CREATE TABLE IF NOT EXISTS posts (
    user_nome text,
    data timestamp,
    conteudo text,
    PRIMARY KEY (user_nome, data)
);
""")

def criar_post(usuario, conteudo):
    session.execute(
        "INSERT INTO posts (user_nome, data, conteudo) VALUES (%s, %s, %s)",
        (usuario, datetime.now(), conteudo)
    )
    print(f"Post criado no Cassandra para {usuario}")

# ---------------- Execução (Teste) ----------------
if __name__ == "__main__":
    criar_usuario("Ana")
    criar_usuario("João")
    
    seguir("João", "Ana")

    criar_post("Ana", "Olá, esse é meu primeiro post!")
