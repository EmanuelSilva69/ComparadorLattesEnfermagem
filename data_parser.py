import re
import os
import json
import glob

CACHE_FILE = "mapeamento_lattes.json"
BASE_DIR_PERFIS = "escavador_perfis"

def extrair_texto_html(html):
    text = html

    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = re.sub(r'/*# sourceMappingURL=data:[^ ]+', '', text)
    text = re.sub(r'data:image/[^;]+;base64[^"]+', '', text)

    desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    meta_desc = desc.group(1) if desc else ""

    text = re.sub(r'<(br|/p|/div|/li|/tr|/h[1-6]|/header|/section|/footer)>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text)

    lines = [l.strip() for l in text.split('\n') if l.strip()]
    lines = [l for l in lines if len(l) > 15]

    result = "\n".join(lines)

    if meta_desc:
        result = f"--- RESUMO ---\n{meta_desc}\n\n--- DETALHES ---\n{result}"

    lines_out = result.split('\n')
    if len(lines_out) > 150:
        lines_out = lines_out[:150]
        result = "\n".join(lines_out) + "\n[...]"

    return result

def load_students(filepath="academicData.ts"):
    """Carrega a lista de alunos a partir do arquivo TypeScript."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    students = []
    # Busca blocos de objetos que tenham nome, defesa, turma e conclusaoNoPrazo
    matches = re.finditer(
        r'nome:\s*\"([^\"]+)\".*?defesa:\s*\"([^\"]*)\".*?conclusaoNoPrazo:\s*\"([^\"]+)\".*?turma:\s*(\d+)',
        content, re.DOTALL
    )
    
    for m in matches:
        nome = m.group(1).strip()
        defesa = m.group(2).strip()
        status = m.group(3).strip()
        turma = int(m.group(4))
        
        # Mostra "EM ANDAMENTO" para alunos sem defesa
        if not defesa:
            defesa = "EM ANDAMENTO"
        
        students.append({
            "nome": nome,
            "defesa": defesa,
            "status": status,
            "turma": turma
        })
            
    return students


def get_aluno_origem(nome_aluno):
    """Verifica se o aluno possui dados JSON (Lattes) ou HTML (Escavador) disponíveis."""
    # --- CANAL 1: JSON do Lattes ---
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_ids = json.load(f)
            id_lattes = cache_ids.get(nome_aluno, "").strip()
            if id_lattes and re.match(r'^\d{16}$', id_lattes):
                json_dir = "scriptLattes/resultados/json"
                arquivos = glob.glob(os.path.join(json_dir, f"*_{id_lattes}.json"))
                if arquivos:
                    return "json"
        except:
            pass

    # --- CANAL 2: HTML do Escavador ---
    nome_pasta_limpo = re.sub(r'[\\/*?:"<>|]', "", nome_aluno)
    caminho_html = os.path.join(BASE_DIR_PERFIS, nome_pasta_limpo, "perfil.html")
    if os.path.exists(caminho_html):
        return "html"

    return "none"

def gerar_lista_alunos_scriptlattes(filename="scriptLattes/lista_alunos.txt"):
    """
    Lê o mapeamento_lattes.json e gera o arquivo de texto de entrada do scriptLattes.
    Coloca na lista APENAS os alunos que possuem o ID Lattes de 16 dígitos válido.
    Formatação estrita exigida pelo scriptLattes: ID_16_DIGITOS , Nome Completo
    """
    if not os.path.exists(CACHE_FILE):
        print(f"⚠️ Arquivo de cache '{CACHE_FILE}' não encontrado. Execute o scraper.py primeiro.")
        return False

    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache_ids = json.load(f)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    linhas_para_salvar = []

    for nome, valor in cache_ids.items():
        # Verifica se o valor guardado é puramente um ID numérico de 16 dígitos
        if valor and re.match(r'^\d{16}$', str(valor).strip()):
            # Salvando no padrão estrito 'ID , Nome' exigido pelo CNPq/scriptLattes
            linhas_para_salvar.append(f"{valor.strip()} , {nome}\n")

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(linhas_para_salvar)
        
    print(f"💾 [DATA PARSER] {len(linhas_para_salvar)} alunos exportados no formato correto (ID , Nome) para: {filename}")
    return True

def get_student_data_from_json(nome_aluno, json_dir="scriptLattes/resultados/json"):
    """
    Busca o arquivo JSON do aluno DIRETAMENTE na subpasta resultados/json/.
    Busca pelo ID de 16 dígitos contido no final do nome do arquivo.
    """
    if not os.path.exists(json_dir):
        return None

    if not os.path.exists(CACHE_FILE):
        return None
        
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_ids = json.load(f)
            
        id_lattes = cache_ids.get(nome_aluno, "").strip()
        
        # Se não for um ID numérico puro de 16 dígitos, ignora (deixa para o Escavador)
        if not id_lattes or not re.match(r'^\d{16}$', id_lattes):
            return None
            
        # Busca o arquivo que termina com o ID de 16 dígitos dentro da pasta json/
        arquivos = glob.glob(os.path.join(json_dir, f"*_{id_lattes}.json"))
        
        if not arquivos:
            return None
            
        with open(arquivos[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        pessoais = data.get('informacoes_pessoais', {})
        markdown_text = f"NOME NO PROJETO: {nome_aluno}\n"
        markdown_text += f"NOME OFICIAL LATTES: {pessoais.get('nome_completo', nome_aluno)}\n"
        markdown_text += f"RESUMO: {pessoais.get('texto_resumo', 'Sem resumo disponível')}\n\n"
        
        markdown_text += "### PROJETOS DE PESQUISA\n"
        for proj in data.get('projetos_pesquisa', []):
            markdown_text += f"- {proj.get('nome', 'Projeto')} ({proj.get('ano_inicio', '')})\n"
            
        markdown_text += "\n### PUBLICAÇÕES\n"
        for art in data.get('producao_bibliografica', {}).get('artigo_em_periodico', []):
            markdown_text += f"- {art.get('titulo', 'Artigo')} ({art.get('ano', '')})\n"
            
        return markdown_text
    except Exception as e:
        print(f"⚠️ Erro ao processar JSON do aluno {nome_aluno}: {e}")
        return None

def obter_conteudo_academico_hibrido(nome_aluno):
    """
    Mecanismo Híbrido de Coleta de Dados para a IA (Canal Principal vs Fallback).
    """
    # --- CANAL 1: Dados Oficiais do scriptLattes ---
    # Apontando explicitamente para a subpasta json/
    dados_lattes = get_student_data_from_json(nome_aluno, json_dir="scriptLattes/resultados/json")
    if dados_lattes:
        return f"--- DADOS OFICIAIS DO CURRÍCULO LATTES (via scriptLattes) ---\n{dados_lattes}"

    # --- CANAL 2: Fallback (Plano B) via HTML do Escavador ---
    nome_pasta_limpo = re.sub(r'[\\/*?:"<>|]', "", nome_aluno)
    caminho_html = os.path.join(BASE_DIR_PERFIS, nome_pasta_limpo, "perfil.html")
    
    if os.path.exists(caminho_html):
        try:
            with open(caminho_html, "r", encoding="utf-8") as f:
                html_bruto = f.read()

            texto_limpo = extrair_texto_html(html_bruto)
            
            return f"--- DADOS PROVENIENTES DO HTML DO ESCAVADOR (FALLBACK) ---\nNOME DO ALUNO: {nome_aluno}\n{texto_limpo}"
        except:
            pass
            
    return None