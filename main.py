"""Exemplo pequeno de RAG com LlamaIndex e ChromaDB persistente."""

import argparse
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.chroma import ChromaVectorStore


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_DIR = ROOT / "storage" / "chroma"
COLLECTION = "base_conhecimento"
EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-2.5-flash"


def configurar_api() -> str:
    load_dotenv(ROOT / ".env")
    chave = os.getenv("GEMINI_API_KEY")
    if not chave or chave == "sua_chave_aqui":
        raise SystemExit("Configure GEMINI_API_KEY no arquivo .env antes de continuar.")
    return chave


def cliente_chroma():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(DB_DIR))


def indexar() -> None:
    arquivos = sorted(
        path for path in DATA_DIR.rglob("*") if path.is_file() and path.suffix.lower() in {".txt", ".md"}
    ) if DATA_DIR.exists() else []
    if not arquivos:
        raise SystemExit("Coloque ao menos um arquivo .txt ou .md na pasta data/.")

    chave = configurar_api()
    documentos = SimpleDirectoryReader(input_files=[str(path) for path in arquivos]).load_data()
    if not documentos:
        raise SystemExit("Nenhum conteúdo foi encontrado nos arquivos da pasta data/.")

    db = cliente_chroma()
    # Recria a coleção para que arquivos removidos não permaneçam nas consultas.
    if any(colecao.name == COLLECTION for colecao in db.list_collections()):
        db.delete_collection(COLLECTION)
    colecao = db.get_or_create_collection(COLLECTION)
    armazenamento = StorageContext.from_defaults(
        vector_store=ChromaVectorStore(chroma_collection=colecao)
    )
    VectorStoreIndex.from_documents(
        documentos,
        storage_context=armazenamento,
        embed_model=GoogleGenAIEmbedding(model_name=EMBEDDING_MODEL, api_key=chave),
    )
    print(f"{len(arquivos)} arquivo(s) indexado(s). {colecao.count()} trecho(s) salvos em {DB_DIR}.")


def perguntar(pergunta: str) -> None:
    chave = configurar_api()
    db = cliente_chroma()
    if not any(colecao.name == COLLECTION for colecao in db.list_collections()):
        raise SystemExit("Base vazia. Execute 'python main.py indexar' primeiro.")
    colecao = db.get_collection(COLLECTION)
    if colecao.count() == 0:
        raise SystemExit("Base vazia. Execute 'python main.py indexar' primeiro.")

    indice = VectorStoreIndex.from_vector_store(
        ChromaVectorStore(chroma_collection=colecao),
        embed_model=GoogleGenAIEmbedding(model_name=EMBEDDING_MODEL, api_key=chave),
    )
    consulta = indice.as_query_engine(
        llm=GoogleGenAI(model=LLM_MODEL, api_key=chave), similarity_top_k=3
    )
    resposta = consulta.query(pergunta)
    print(f"\nResposta:\n{resposta}\n")
    fontes = sorted({
        Path(no.node.metadata["file_path"]).name
        for no in resposta.source_nodes
        if no.node.metadata.get("file_path")
    })
    if fontes:
        print("Fontes: " + ", ".join(fontes))


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG simples com ChromaDB e LlamaIndex")
    comandos = parser.add_subparsers(dest="comando", required=True)
    comandos.add_parser("indexar", help="Lê data/ e grava os vetores em storage/")
    consulta = comandos.add_parser("perguntar", help="Consulta a base já indexada")
    consulta.add_argument("pergunta", help="Pergunta em linguagem natural")
    args = parser.parse_args()

    if args.comando == "indexar":
        indexar()
    else:
        perguntar(args.pergunta)


if __name__ == "__main__":
    main()
