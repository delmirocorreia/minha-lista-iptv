import undetected_chromedriver as uc
import re
import time
import base64
import os
GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")
from github import Github
from github import Auth

# --- CONFIGURAÇÕES ---
ARQUIVO_M3U = "index.m3u"
URL_BASE = "https://ww2.embedtv.lat/"

REPO_NAME = "delmirocorreia/minha-lista-iptv" # Seu usuário/nome do repositório

def atualizar_repositorio(novo_conteudo):
    try:
        # Forma moderna e correta de autenticar
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        repo = g.get_repo(REPO_NAME)
        
        conteudo_arquivo = repo.get_contents(ARQUIVO_M3U)
        
        repo.update_file(
            path=conteudo_arquivo.path,
            message="Automação: Atualizando lista de canais",
            content=novo_conteudo,
            sha=conteudo_arquivo.sha
        )
        print("🚀 Repositório GitHub Pages atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar GitHub: {e}")

def processar_m3u():
    with open(ARQUIVO_M3U, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    options = uc.ChromeOptions()
    options.add_argument("--headless=new") # Importante para rodar no servidor
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Removido version_main=148 para não dar erro
    driver = uc.Chrome(options=options)

    for i in range(len(linhas)):
        if '#EXTINF' in linhas[i] and 'tvg-id="' in linhas[i]:
            canal_id = re.search(r'tvg-id="([^"]+)"', linhas[i]).group(1)
            url_antiga = linhas[i+1].strip()

            if "embedtv" in url_antiga:
                print(f"🔄 Checando {canal_id}...")
                driver.get(f"{URL_BASE}{canal_id}")
                time.sleep(5)
                
                html = driver.page_source
                # Busca pelo link .css como você solicitou
                match = re.search(r'(https:[^"\']*?style\.css)', html, re.IGNORECASE)
                
                if match:
                    url_nova = match.group(1)
                    if url_nova != url_antiga:
                        print(f"✨ Atualizado: {canal_id}")
                        linhas[i+1] = url_nova + "\n"
                else:
                    print(f"⚠️ Não há atualização para {canal_id}")

    driver.quit()
    
    # Salva o arquivo local e envia para o GitHub
    novo_conteudo = "".join(linhas)
    with open(ARQUIVO_M3U, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    
    atualizar_repositorio(novo_conteudo)

if __name__ == "__main__":
    processar_m3u()
