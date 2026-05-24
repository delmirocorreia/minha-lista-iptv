import undetected_chromedriver as uc
import chromedriver_autoinstaller
import re
import time
import os
from github import Github, Auth

# --- CONFIGURAÇÕES ---
ARQUIVO_M3U = "index.m3u"
URL_BASE = "https://ww2.embedtv.lat/"
REPO_NAME = "delmirocorreia/minha-lista-iptv"
GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")

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
   # 1. Instalação e configuração do Chrome dentro da função
    driver_path = chromedriver_autoinstaller.install() 
    
    options = uc.ChromeOptions()
    options.add_argument("--incognito")  # Abre em modo anônimo, sem cache
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = uc.Chrome(options=options, driver_executable_path=driver_path)
    
    # 2. Leitura do arquivo
    with open(ARQUIVO_M3U, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    # 3. Loop de processamento... (Seu código existente)
    for i in range(len(linhas)):
        if '#EXTINF' in linhas[i] and 'tvg-id="' in linhas[i]:
            canal_id = re.search(r'tvg-id="([^"]+)"', linhas[i]).group(1)
            url_antiga = linhas[i+1].strip()

            if "embedtv" in url_antiga:
                print(f"🔄 Checando {canal_id}...")
                driver.get(f"{URL_BASE}{canal_id}")
                # Aguarda até 10 segundos até que o elemento CSS apareça
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC

                try:
                    # Espera algo específico da página carregar (ex: um elemento que contenha 'style')
                    WebDriverWait(driver, 10).until(
                        lambda d: "style.css" in d.page_source
                    )
                except:
                    print(f"⚠️ Timeout: Não encontrei 'style.css' na página de {canal_id}")
                
                html = driver.page_source
                if "style.css" not in html:
                    print(f"DEBUG: O código fonte de {canal_id} NÃO contém 'style.css'.")
                    
                # Busca pelo link .css
                match = re.search(r'(https?://[^\s"\'<>]+style\.css)', html, re.IGNORECASE)
                
                if match:
                    url_nova = match.group(1)
                    if url_nova != url_antiga:
                        print(f"✨ Atualizado: {canal_id}")
                        linhas[i+1] = url_nova + "\n"
                else:
                    print(f"⚠️ Não há atualização para o canal {canal_id}")

    driver.quit()

    # 4. Atualização    
    # Salva o arquivo local e envia para o GitHub
    novo_conteudo = "".join(linhas)
    atualizar_repositorio(novo_conteudo)
    
if __name__ == "__main__":
      processar_m3u()
