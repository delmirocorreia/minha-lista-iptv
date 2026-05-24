import undetected_chromedriver as uc
import time
import os
import json
from github import Github, Auth

# --- CONFIGURAÇÕES ---
URL_BASE = "https://ww2.embedtv.lat/"
REPO_NAME = "delmirocorreia/minha-lista-iptv" 
GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")

def processar_espelho():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)

    # 1. Configuração Correta de Log de Performance
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # É OBRIGATÓRIO definir o loggingPrefs aqui, antes de iniciar o driver
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options, version_main=148)
    
    try:
        driver.get(f"{URL_BASE}discoverychannel")
        time.sleep(20)
        
        # Agora o get_log('performance') deve funcionar
        logs = driver.get_log('performance')
        
        urls_capturadas = []
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                if log['method'] == 'Network.responseReceived':
                    url = log['params']['response']['url']
                    urls_capturadas.append(url)
            except:
                continue
        
        # Filtra apenas o que parece ser CSS
        debug_output = "\n".join([u for u in urls_capturadas if ".css" in u])
        
        with open("debug_espelho.txt", "w", encoding="utf-8") as f:
            f.write(f"--- URLS DE CSS ENCONTRADAS NA REDE ---\n\n{debug_output}")

        with open("debug_espelho.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()

        try:
            file_info = repo.get_contents("debug_espelho.txt")
            repo.update_file(file_info.path, "Debug: Captura Rede [skip ci]", conteudo, file_info.sha)
        except:
            repo.create_file("debug_espelho.txt", "Debug: Captura Rede [skip ci]", conteudo)
            
    finally:
        driver.quit()

if __name__ == "__main__":
    processar_espelho()
