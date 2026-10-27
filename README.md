# Chatbot RAG da Loja Nexa

Projeto introdutório de **Retrieval-Augmented Generation (RAG)** em Python. O chatbot responde perguntas sobre uma loja fictícia usando uma base de conhecimento em texto. O LlamaIndex organiza a leitura e a recuperação dos documentos, o ChromaDB persiste os trechos pesquisáveis e a API Gemini gera a resposta.

O projeto foi inspirado na [Aceleração Santander — RAG com ChromaDB, LlamaIndex e Python](https://www.dio.me/acceleration/santander-rag-com-chromadb-llamaindex-e-python), da DIO. Esta implementação é independente e foi mantida pequena para fins de estudo.

## Funcionalidades

- Indexa arquivos `.txt` e `.md` colocados em `data/`.
- Salva os trechos e embeddings no ChromaDB local, para reutilizá-los em consultas futuras.
- Recebe perguntas pelo terminal e mostra a resposta junto ao nome do arquivo recuperado.
- Inclui uma base fictícia da Loja Nexa com catálogo, atendimento, pagamentos, entregas, trocas, garantia e pedidos demonstrativos.

```text
Documentos em data/ → LlamaIndex → embeddings Gemini → ChromaDB em storage/
Pergunta → busca no ChromaDB → trechos relevantes → Gemini → resposta + fonte
```

## Tecnologias

| Tecnologia | Papel no projeto |
| --- | --- |
| Python | Executa os comandos de indexação e consulta. |
| LlamaIndex | Lê os documentos, cria o índice e monta a consulta RAG. |
| ChromaDB | Armazena localmente os trechos e embeddings. |
| Gemini | Cria embeddings com `gemini-embedding-001` e respostas com `gemini-2.5-flash`. |

## Pré-requisitos

- Python 3.12, versão usada no desenvolvimento.
- Uma [chave da API Gemini](https://ai.google.dev/gemini-api/docs/api-key) com acesso aos modelos acima. O uso da API pode gerar cobrança conforme a conta e o volume de chamadas.

## Instalação

Clone o repositório, entre na pasta que contém `main.py` e crie um ambiente virtual.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

**macOS ou Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Abra o arquivo `.env` e substitua `sua_chave_aqui` pela sua chave Gemini:

```dotenv
GEMINI_API_KEY=sua_chave_aqui
```

O `.env` contém um segredo e está ignorado pelo Git. Não coloque a chave no código, em capturas de tela ou em commits. O diretório `storage/` e o ambiente `.venv/` também não entram no repositório.

Se o Cursor ou VS Code marcar os imports como ausentes, use **Python: Select Interpreter** e escolha o Python de `.venv/`.

## Como usar

Na raiz do projeto, execute primeiro a indexação:

```powershell
python main.py indexar
```

Depois, faça uma pergunta:

```powershell
python main.py perguntar "O mouse M200 tem Bluetooth?"
```

Você também pode perguntar sobre frete, descontos, horários de atendimento e os pedidos demonstrativos. O programa exibe os nomes dos arquivos usados como fonte. No macOS ou Linux, substitua `python` por `python3` caso seja esse o comando disponível.

Para mudar a base, adicione, edite ou remova arquivos `.txt` e `.md` em `data/` e execute `indexar` novamente. Esse comando **recria a coleção** do ChromaDB com o conteúdo atual da pasta. O comando `perguntar` usa os vetores já salvos e não reindexa os documentos a cada pergunta.

## Estrutura do projeto

```text
.
├── data/
│   └── base_conhecimento_loja_nexa.txt  # dados fictícios para consulta
├── main.py                                # CLI: indexar e perguntar
├── requirements.txt                       # bibliotecas Python
├── .env.example                           # exemplo de configuração
├── .gitignore                              # arquivos locais fora do Git
├── .venv/                                 # criado na instalação; ignorado
└── storage/                               # criado na indexação; ignorado
```

## Limites do exemplo

A base da Loja Nexa é **inteiramente fictícia** e seus pedidos demonstrativos são registros estáticos de 20/10/2026. O chatbot não consulta estoque, entregas, pagamentos ou pedidos reais, nem executa ações nesses sistemas.

A consulta recupera até três trechos por pergunta. O nome do arquivo mostrado como fonte indica de onde vieram os trechos recuperados, mas não garante que cada frase da resposta esteja correta. Como não há uma regra rígida de recusa para assuntos ausentes da base, confira respostas importantes no documento original.

## Referências

- [Aceleração Santander — RAG com ChromaDB, LlamaIndex e Python](https://www.dio.me/acceleration/santander-rag-com-chromadb-llamaindex-e-python)
- [Documentação do LlamaIndex para ChromaDB](https://developers.llamaindex.ai/python/framework/understanding/rag/storing/)
- [Documentação do ChromaDB: clientes persistentes](https://cookbook.chromadb.dev/core/clients/)
