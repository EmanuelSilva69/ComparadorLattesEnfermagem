import ollama

MODEL_NAME = "phi3.5:3.8b" 

def analyze_profile_with_llm(conteudo_bruto, data_defesa):
    """Analisa o JSON do Lattes ou o HTML do Escavador usando o modelo local 9B."""
    
    prompt = f"""Você é um Analista de Dados Acadêmicos Sênior especializado em mapeamento de egressos.
Sua tarefa é analisar o histórico fornecido e identificar todas as atividades realizadas EXCLUSIVAMENTE APÓS a data de sua defesa de mestrado.

### DIRETRIZES DE PROCESSAMENTO:
1. O texto fornecido pode ser um resumo estruturado ou o código HTML bruto da plataforma Escavador. Ignore tags HTML e processe apenas o texto legível.
2. Identifique e memorize a data de corte (Defesa do Mestrado): {data_defesa}
3. Filtre a linha do tempo e ignore tudo o que aconteceu ANTES ou DURANTE o Mestrado.

---
### ENTRADA DOS DADOS:
<data_defesa_mestrado>{data_defesa}</data_defesa_mestrado>
<conteudo_academico_bruto>{conteudo_bruto}</conteudo_academico_bruto>
---

### RESUMO EXECUTIVO (MÁXIMO 4 LINHAS):
"""
    
    try:
        client = ollama.Client(host="http://127.0.0.1:11434")
        
        response = client.chat(
            model=MODEL_NAME, 
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um assistente acadêmico objetivo focado em análise temporal de currículos estruturados e dumps de HTML."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            # 🔥 CORREÇÃO CRÍTICA: Expande a janela de contexto para 16k tokens para caber o HTML
            options={
                "num_ctx": 16384
            }
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"Erro de comunicação com Ollama: {e}"