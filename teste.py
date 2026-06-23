import os
import json
import re
from data_parser import load_students, obter_conteudo_academico_hibrido
from llm import analyze_profile_with_llm

def rodar_teste_unitario():
    print("=" * 60)
    print("🧪 TESTE INTEGRAL DE PIPELINE (DADOS ➡️ IA ➡️ FORMATO)")
    print("=" * 60)

    # 1. Carrega Alunos
    alunos = load_students()
    if not alunos:
        print("❌ Nenhum aluno carregado do academicData.ts")
        return
    
    # Seleciona o primeiro da lista para o teste
    aluno_teste = alunos[0]
    nome = aluno_teste["nome"]
    defesa = aluno_teste["defesa"]
    
    print(f"📋 Aluno Alvo do Teste: {nome}")
    print(f"📅 Data de Defesa Clicada: {defesa}")
    print("-" * 60)

    # 2. Teste do Data Parser (Busca Híbrida)
    print("🔄 Etapa 1: Buscando repositório de dados locais...")
    contexto_bruto = obter_conteudo_academico_hibrido(nome)
    
    if not contexto_bruto:
        print("❌ Falha na Etapa 1: Dados não localizados em nenhuma das pastas.")
        return
    
    origem = "Lattes (JSON)" if "via scriptLattes" in contexto_bruto else "Escavador (HTML)"
    print(f"✅ Etapa 1 Sucesso! Origem identificada: {origem}")
    print(f"📦 Tamanho do payload enviado: {len(contexto_bruto)} caracteres.")
    print("-" * 60)

    # 3. Teste do Envio e Retorno da IA
    print("🧠 Etapa 2: Enviando payload ao Ollama (phi3.5:3.8b)... Aguarde...")
    try:
        resposta_ia = analyze_profile_with_llm(contexto_bruto, defesa)
        print("✅ Etapa 2 Sucesso! Resposta da IA recebida.")
    except Exception as e:
        print(f"❌ Falha na Etapa 2 (Comunicação LLM): {e}")
        return
    print("-" * 60)

    # 4. Formatação do Output para o Front-end
    print("📦 Etapa 3: Simulando empacotamento JSON para o Front-end...")
    objeto_saida = {
        "nome": nome,
        "data_defesa": defesa,
        "origem": origem,
        "resumo_ia": resposta_ia
    }
    
    print("\n👇 JSON FINAL PRONTO PARA O JAVASCRIPT CONSUMIR:")
    print(json.dumps(objeto_saida, indent=4, ensure_ascii=False))
    print("=" * 60)

if __name__ == "__main__":
    rodar_teste_unitario()