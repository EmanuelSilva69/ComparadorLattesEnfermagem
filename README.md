# Scanner Pós-Mestrado Pro v2.0.0

Pipeline híbrido de extração e análise de atividades acadêmicas de egressos de pós-graduação, combinando dados oficiais do Lattes (CNPq) com fallback para perfis do Escavador.com, processados por IA local via Ollama.

## Arquitetura

```
Frontend (index.html) → API (FastAPI) → Data Parser → LLM local (Ollama)
                         ↑                          ↓
              academicData.ts            scriptLattes JSON / Escavador HTML
```

## Requisitos

- **Python 3.10+**
- **Ollama** com modelo baixado: `phi3.5:3.8b`
- Navegador moderno (para o frontend)

## Instalação

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Instalar o Ollama (se não tiver)
# https://ollama.com/download

# Baixar o modelo LLM
ollama pull phi3.5:3.8b
```

## Execução

```bash
python api.py
```

Acessar em: http://localhost:8000

## Como funciona

1. **Base de alunos**: `academicData.ts` contém ~165 egressos com nome e data de defesa.
2. **Busca híbrida**: Para cada aluno, tenta primeiro o JSON do Lattes (via scriptLattes). Se não encontrar, usa o HTML do Escavador como fallback.
3. **Análise por IA**: O conteúdo é enviado para o modelo local `phi3.5:3.8b` (via Ollama), que extrai e resume as atividades realizadas APÓS a defesa do mestrado.
4. **Frontend**: Interface SPA em vanilla JS que lista os alunos e exibe os resumos gerados pela IA.

## Rotas da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/alunos` | Lista todos os alunos |
| GET | `/api/analisar/{nome}` | Analisa um aluno específico |
| POST | `/api/update/lattes` | Atualiza JSONs via scriptLattes (background) |
| POST | `/api/update/escavador` | Atualiza HTMLs via scraper (background) |
| GET | `/` | Frontend SPA |

## Estrutura

```
├── api.py                 # FastAPI backend
├── llm.py                 # Integração com Ollama (phi3.5:3.8b)
├── data_parser.py         # Carregamento e busca híbrida de dados
├── scraper.py             # Selenium scraper para Escavador
├── teste.py               # Teste unitário do pipeline
├── academicData.ts        # Cadastro dos alunos
├── mapeamento_lattes.json # Cache de IDs Lattes / URLs Escavador
├── public/
│   └── index.html         # Frontend SPA
└── scriptLattes/          # Ferramenta de extração Lattes
```

## Tecnologias

- **Backend**: FastAPI + Uvicorn
- **LLM**: Phi-3.5 (3.8B) via Ollama (local, sem API keys)
- **Frontend**: HTML/CSS/JS vanilla
- **Scraping**: Selenium + Chrome
- **Dados**: scriptLattes (CNPq) + Escavador.com

## Autor

Emanuel Silva
