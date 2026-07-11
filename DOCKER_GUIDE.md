# Guia de Implantação com Docker — Scanner Pós-Mestrado

## Requisitos

- Docker Engine 24+ com Docker Compose v2
- GPU NVIDIA com drivers e `nvidia-container-toolkit` (opcional, mas recomendado para rodar LLMs localmente)
- ~8 GB de RAM disponível para o container do Ollama
- 10 GB de espaço livre em disco

---

## 1. Clonar o repositório

```bash
git clone https://github.com/EmanuelSilva69/ComparadorLattesEnfermagem.git
cd ComparadorLattesEnfermagem
```

---

## 2. Colocar os arquivos de dados

Copiar para a raiz do projeto:

| Arquivo | Obrigatório | Descrição |
|---|---|---|
| `academicData.ts` | Sim | Lista de alunos |
| `mapeamento_lattes.json` | Sim | Mapeamento de IDs Lattes |
| `escavador_perfis/` | Não (gera depois) | Perfis HTML de fallback do Escavador |

---

## 3. Subir os containers

```bash
docker compose up -d
```

Isso sobe dois containers:
- **ollama** — Servidor de LLM na porta 11434
- **scanner-pos-mestrado** — Aplicação FastAPI na porta 8000

Para ver os logs:

```bash
docker compose logs -f
```

---

## 4. Baixar os modelos de IA

Assim que o container do Ollama estiver rodando (`docker compose ps`), baixar os modelos:

```bash
# Phi-3.5 (padrão, ~2.3 GB)
docker exec ollama ollama pull phi3.5:3.8b

# VibeThinker-3B (alternativa, ~1.8 GB)
docker exec ollama ollama pull hf.co/prithivMLmods/VibeThinker-3B-GGUF:F16
```

Verificar se os modelos foram baixados:

```bash
docker exec ollama ollama list
```

---

## 5. Acessar a aplicação

```
http://<IP-DO-SERVIDOR>:8000
```

### Endpoints úteis

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/alunos` | Lista todos os alunos com a origem dos dados |
| GET | `/api/analisar/{nome}?modelo=phi3` | Analisa um aluno com Phi-3.5 |
| GET | `/api/analisar/{nome}?modelo=vibethinker` | Analisa um aluno com VibeThinker-3B |
| POST | `/api/update/lattes` | Dispara extração Lattes em segundo plano |
| POST | `/api/update/escavador` | Dispara extração Escavador em segundo plano |

---

## 6. Atualizar a base de dados (primeira vez)

### 6.1 Buscar IDs Lattes e HTMLs de fallback

```bash
docker exec scanner-pos-mestrado python scraper.py
```

Esse script:
1. Varre a lista de alunos do `academicData.ts`
2. Busca perfis no Escavador via Google
3. Salva os HTMLs em `escavador_perfis/` e os IDs no `mapeamento_lattes.json`

### 6.2 Extrair dados estruturados do Lattes (opcional)

Se houver IDs Lattes de 16 dígitos no `mapeamento_lattes.json`:

```bash
docker exec scanner-pos-mestrado python -c "from data_parser import gerar_lista_alunos_scriptlattes; gerar_lista_alunos_scriptlattes()"
docker exec -w /app/scriptLattes scanner-pos-mestrado python scriptLattes.py exemplo/teste-01.config
```

---

## 7. Parar os containers

```bash
docker compose down
```

Para remover também os volumes (dados dos modelos serão perdidos):

```bash
docker compose down -v
```

---

## 8. Observações

- **Sem GPU:** O Ollama funciona em CPU, mas será muito lento. Remova o bloco `deploy.resources` do `docker-compose.yml` se não tiver NVIDIA.
- **Firewall:** Liberar a porta 8000 no firewall da instituição.
- **Proxy reverso:** Para produção, recomenda-se colocar um nginx na frente fazendo proxy para `localhost:8000`.
- **Atualizações:** Para atualizar o código, basta `git pull` e `docker compose up -d --build`.
