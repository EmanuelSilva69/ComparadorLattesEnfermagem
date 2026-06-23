import os
import json
import re
from data_parser import load_students, obter_conteudo_academico_hibrido

def inspecionar_contexto_ia():
    print("=" * 60)
    print("🧪 SCRIPT DE TESTE: INSPEÇÃO DE CONTEXTO DA IA")
    print("=" * 60)
    
    # 1. Carrega os alunos oficiais
    if not os.path.exists("academicData.ts"):
        print("❌ Arquivo 'academicData.ts' não encontrado na raiz.")
        return
    
    alunos = load_students()
    print(f"📊 Total de alunos carregados do academicData.ts: {len(alunos)}")

    # 2. Carrega o cache de IDs para escolher os alvos de teste
    cache_file = "mapeamento_lattes.json"
    if not os.path.exists(cache_file):
        print(f"❌ Arquivo '{cache_file}' não encontrado.")
        return
        
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    alvo_lattes = None
    alvo_escavador = None

    # Encontra o primeiro aluno de cada tipo para o teste
    for aluno in alunos:
        nome = aluno['nome']
        valor = str(cache.get(nome, "")).strip()
        
        if re.match(r'^\d{16}$', valor) and not alvo_lattes:
            alvo_lattes = nome
        elif valor.startswith("ESCAVADOR:") and not alvo_escavador:
            alvo_escavador = nome

    # --- TESTE 1: ALUNO DO LATTES (JSON SUBPASTA) ---
    if alvo_lattes:
        print("\n" + "-"*50)
        print(f"📡 TESTANDO CANAL 1: Currículo Lattes (JSON)")
        print(f"Aluno Selecionado: {alvo_lattes}")
        print(f"ID Mapeado: {cache[alvo_lattes]}")
        print("-"*50)
        
        # Executa o extrator híbrido
        conteudo_lattes = obter_conteudo_academico_hibrido(alvo_lattes)
        
        if conteudo_lattes:
            print("👇 TEXTO COMPLETO QUE ENTRA NO CONTEXTO DA IA:")
            print(conteudo_lattes)
        else:
            print("❌ ERRO: O Python não achou o arquivo JSON na pasta 'scriptLattes/resultados/json/'.")
    else:
        print("\n🟡 Nenhum aluno com ID Lattes de 16 dígitos encontrado para teste.")

    # --- TESTE 2: ALUNO DO ESCAVADOR (HTML BRUTO) ---
    if alvo_escavador:
        print("\n" + "-"*50)
        print(f"🌐 TESTANDO CANAL 2: Fallback Contingência (HTML)")
        print(f"Aluno Selecionado: {alvo_escavador}")
        print("-"*50)
        
        # Executa o extrator híbrido
        conteudo_escavador = obter_conteudo_academico_hibrido(alvo_escavador)
        
        if conteudo_escavador:
            print("👇 TRECHO DO HTML QUE ENTRA NO CONTEXTO DA IA (Truncado para inspeção):")
            # Mostra apenas as primeiras 15 linhas do dump HTML para não inundar o terminal
            linhas = conteudo_escavador.splitlines()
            print("\n".join(linhas[:20]))
            print(f"\n... [Mais {len(linhas) - 20} linhas de código HTML bruto enviadas ao Ollama] ...")
        else:
            print(f"❌ ERRO: Arquivo 'perfil.html' ausente na pasta 'escavador_perfis/{alvo_escavador}/'.")
    else:
        print("\n🟡 Nenhum aluno mapeado via Escavador encontrado para teste.")

    print("\n" + "=" * 60)
    print("🎉 FIM DA INSPEÇÃO DE DADOS")
    print("=" * 60)

if __name__ == "__main__":
    inspecionar_contexto_ia()