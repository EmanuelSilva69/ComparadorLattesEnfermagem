import ollama

MODEL_NAME = "phi3.5:3.8b" 

def analyze_profile_with_llm(conteudo_bruto, data_defesa):
    prompt = f"""Dados academicos (data de corte: {data_defesa}):

{conteudo_bruto}

-- ACIMA OS DADOS. ABAIXO, 4 LINHAS NO FORMATO:
1. Doutorado: SIM (instituicao, ano) ou NAO
2. Trabalho atual (cargo, instituicao)
3. Tema geral das pesquisas + ano
4. Tema geral das pesquisas + ano"""
    try:
        return ollama.Client(host="http://127.0.0.1:11434").chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "4 linhas exatas. Sem notas, bullets ou explicacoes."},
                {"role": "user", "content": prompt}
            ],
            options={"num_ctx": 8192}
        )['message']['content'].strip()
    except Exception as e:
        return f"Erro de comunicação com Ollama: {e}"