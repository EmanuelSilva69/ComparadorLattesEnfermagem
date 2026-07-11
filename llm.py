import ollama
import re

MODEL_NAME = "phi3.5:3.8b"
ALTERNATIVE_MODELS = {
    "vibethinker": "hf.co/prithivMLmods/VibeThinker-3B-GGUF:F16",
    "phi3": "phi3.5:3.8b",
}

def _strip_raciocinio(texto):
    texto = re.sub(r'<think>.*?</think>', '', texto, flags=re.DOTALL)
    texto = re.sub(r'\[/?(INST|THINK|REASON|ANALISE|PENSE|RACIOCINIO)\]', '', texto, flags=re.IGNORECASE)
    linhas = texto.strip().split('\n')
    resultado = []
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        if re.match(r'^(Doutorado|1[.)]|1[.:]|Trabalho atual|2[.)]|2[.:]|Tema geral|3[.)]|3[.:]|4[.)]|4[.:])', linha, re.IGNORECASE):
            resultado.append(linha)
        elif resultado:
            resultado.append(linha)
    if not resultado:
        resultado = [l.strip() for l in linhas if l.strip()][-4:]
    return '\n'.join(resultado)

def analyze_profile_with_llm(conteudo_bruto, data_defesa, model_key="phi3"):
    model = ALTERNATIVE_MODELS.get(model_key, MODEL_NAME)
    prompt = f"""Dados academicos (data de corte: {data_defesa}):

{conteudo_bruto}

-- ACIMA OS DADOS. ABAIXO, 4 LINHAS NO FORMATO:
1. Doutorado: SIM (instituicao, ano) ou NAO
2. Trabalho atual (cargo, instituicao)
3. Tema geral das pesquisas + ano
4. Tema geral das pesquisas + ano"""
    try:
        raw = ollama.Client(host="http://127.0.0.1:11434").chat(
            model=model,
            messages=[
                {"role": "system", "content": "Responda APENAS as 4 linhas. Nenhum raciocinio, nenhuma explicacao, nenhum pensamento antes ou depois. So as 4 linhas."},
                {"role": "user", "content": prompt}
            ],
            options={"num_ctx": 8192, "temperature": 0.0}
        )['message']['content'].strip()
        return _strip_raciocinio(raw)
    except Exception as e:
        return f"Erro de comunicação com Ollama ({model}): {e}"

def analyze_with_vibethinker(conteudo_bruto, data_defesa):
    return analyze_profile_with_llm(conteudo_bruto, data_defesa, model_key="vibethinker")