import os
import sys
import subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import uvicorn

from data_parser import load_students, get_aluno_origem, obter_conteudo_academico_hibrido, gerar_lista_alunos_scriptlattes
from llm import analyze_profile_with_llm, analyze_with_vibethinker

app = FastAPI(title="Scanner Pós-Mestrado API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AlunoResponse(BaseModel):
    nome: str
    defesa: str
    status: str = ""
    turma: int = 0
    origem: str = "none"

@app.get("/api/alunos", response_model=List[AlunoResponse])
def listar_alunos():
    try:
        alunos = load_students()
        for aluno in alunos:
            aluno["origem"] = get_aluno_origem(aluno["nome"])
        return alunos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analisar/{nome}")
def analisar_aluno(nome: str, modelo: str = "phi3"):
    alunos = load_students()
    aluno_alvo = next((a for a in alunos if a["nome"].strip().upper() == nome.strip().upper()), None)
    
    if not aluno_alvo:
        raise HTTPException(status_code=404, detail="Aluno não encontrado na base de dados.")
        
    conteudo = obter_conteudo_academico_hibrido(aluno_alvo["nome"])
    if not conteudo:
        return {
            "nome": aluno_alvo["nome"],
            "defesa": aluno_alvo["defesa"],
            "origem": "Não Encontrado",
            "resumo": "Nenhum registro local (JSON ou HTML) localizado no disco."
        }
        
    origem = "Lattes (JSON)" if "via scriptLattes" in conteudo else "Escavador (HTML)"

    if modelo == "vibethinker":
        resumo_ia = analyze_with_vibethinker(conteudo, aluno_alvo["defesa"])
    else:
        resumo_ia = analyze_profile_with_llm(conteudo, aluno_alvo["defesa"])
    
    return {
        "nome": aluno_alvo["nome"],
        "defesa": aluno_alvo["defesa"],
        "origem": origem,
        "modelo": modelo,
        "resumo": resumo_ia
    }

# --- NOVAS ROTAS DE ATUALIZAÇÃO DE BASE EM SEGUNDO PLANO ---

def tarefa_atualizar_lattes():
    """Roda o scriptLattes no terminal de fundo."""
    print("\n[SISTEMA] Iniciando atualização do Lattes...")
    if gerar_lista_alunos_scriptlattes():
        subprocess.run([sys.executable, "scriptLattes.py", "exemplo/teste-01.config"], cwd="scriptLattes")
        print("\n[SISTEMA] Atualização do Lattes finalizada!")

def tarefa_atualizar_escavador():
    """Roda o scraper.py no terminal de fundo."""
    print("\n[SISTEMA] Iniciando extração do Escavador...")
    subprocess.run([sys.executable, "scraper.py"])
    print("\n[SISTEMA] Extração do Escavador finalizada!")

@app.post("/api/update/lattes")
def update_lattes(background_tasks: BackgroundTasks):
    background_tasks.add_task(tarefa_atualizar_lattes)
    return {"status": "Processo do Lattes iniciado no terminal."}

@app.post("/api/update/escavador")
def update_escavador(background_tasks: BackgroundTasks):
    background_tasks.add_task(tarefa_atualizar_escavador)
    return {"status": "Processo do Escavador iniciado no terminal."}

# --- ARQUIVOS ESTÁTICOS ---
os.makedirs("public", exist_ok=True)

if os.path.exists("public/static"):
    app.mount("/static", StaticFiles(directory="public/static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("public/index.html")

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)