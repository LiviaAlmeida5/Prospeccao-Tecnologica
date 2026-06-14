from pymongo import MongoClient
from neo4j import GraphDatabase
from collections import deque
import random
import time
import statistics


# CONFIGURAÇÕES

NUM_USUARIOS = 1000
SEGUIDOS_POR_USUARIO = 10
PROFUNDIDADE = 4
REPETICOES = 10


# CONEXÕES

mongo = MongoClient("mongodb://localhost:27017")

mongo_db = mongo["benchmark"]
usuarios = mongo_db["usuarios"]

neo4j_driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "senha123")
)

# POPULAR MONGODB


def popular_mongo():

    print("Limpando MongoDB...")
    usuarios.delete_many({})

    print("Criando documentos MongoDB...")

    nomes = [f"Usuario{i}" for i in range(NUM_USUARIOS)]

    docs = []

    for nome in nomes:

        possiveis = [x for x in nomes if x != nome]

        segue = random.sample(
            possiveis,
            SEGUIDOS_POR_USUARIO
        )

        docs.append({
            "nome": nome,
            "segue": segue
        })

    usuarios.insert_many(docs)

    usuarios.create_index("nome")

    print("MongoDB populado.\n")


# POPULAR NEO4J


def popular_neo4j():

    print("Limpando Neo4j...")

    with neo4j_driver.session() as session:

        session.run("""
        MATCH (n)
        DETACH DELETE n
        """)

        session.run("""
        CREATE CONSTRAINT user_nome_unique
        IF NOT EXISTS
        FOR (u:User)
        REQUIRE u.nome IS UNIQUE
        """)

    print("Criando nós Neo4j...")

    with neo4j_driver.session() as session:

        for i in range(NUM_USUARIOS):

            session.run(
                """
                MERGE (:User {nome:$nome})
                """,
                nome=f"Usuario{i}"
            )

    print("Criando relacionamentos Neo4j...")

    with neo4j_driver.session() as session:

        for doc in usuarios.find():

            origem = doc["nome"]

            for destino in doc["segue"]:

                session.run("""
                MATCH (a:User {nome:$origem})
                MATCH (b:User {nome:$destino})
                MERGE (a)-[:SEGUE]->(b)
                """,
                origem=origem,
                destino=destino)

    print("Neo4j populado.\n")

# CONSULTA MONGODB

def consulta_mongo(usuario_inicial):

    inicio = time.perf_counter()

    visitados = set()

    fila = deque()
    fila.append((usuario_inicial, 0))

    while fila:

        atual, profundidade = fila.popleft()

        if profundidade >= PROFUNDIDADE:
            continue

        doc = usuarios.find_one(
            {"nome": atual},
            {"_id": 0, "segue": 1}
        )

        if not doc:
            continue

        for proximo in doc["segue"]:

            if proximo not in visitados:

                visitados.add(proximo)

                fila.append(
                    (proximo, profundidade + 1)
                )

    fim = time.perf_counter()

    return (fim - inicio) * 1000, len(visitados)

# CONSULTA NEO4J

def consulta_neo4j(usuario):

    inicio = time.perf_counter()

    with neo4j_driver.session() as session:

        resultado = session.run(f"""
        MATCH (u:User {{nome:$nome}})
              -[:SEGUE*1..{PROFUNDIDADE}]->
              (destino)

        RETURN count(DISTINCT destino) AS total
        """,
        nome=usuario)

        total = resultado.single()["total"]

    fim = time.perf_counter()

    return (fim - inicio) * 1000, total

# BENCHMARK

def benchmark():

    tempos_mongo = []
    tempos_neo4j = []

    print("Executando benchmark...\n")

    for i in range(REPETICOES):

        tempo_mongo, total_mongo = consulta_mongo("Usuario0")
        tempo_neo4j, total_neo4j = consulta_neo4j("Usuario0")

        tempos_mongo.append(tempo_mongo)
        tempos_neo4j.append(tempo_neo4j)

        print(
            f"Execução {i+1:02d} | "
            f"Mongo: {tempo_mongo:.2f} ms | "
            f"Neo4j: {tempo_neo4j:.2f} ms"
        )

    media_mongo = statistics.mean(tempos_mongo)
    media_neo4j = statistics.mean(tempos_neo4j)

    print("\n==============================")
    print("RESULTADO FINAL")
    print("==============================")

    print(f"MongoDB média : {media_mongo:.2f} ms")
    print(f"Neo4j média   : {media_neo4j:.2f} ms")

    if media_neo4j < media_mongo:

        ganho = media_mongo / media_neo4j

        print(
            f"\nNeo4j foi "
            f"{ganho:.2f}x mais rápido."
        )

    else:

        ganho = media_neo4j / media_mongo

        print(
            f"\nMongoDB foi "
            f"{ganho:.2f}x mais rápido."
        )


# MAIN

if __name__ == "__main__":

    popular_mongo()

    popular_neo4j()

    benchmark()

    neo4j_driver.close()
