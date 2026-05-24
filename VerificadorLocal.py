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

    # Configuração para extrair logs de rede via CDP
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    driver = uc.Chrome(options=options, version_main=148)
    
    try:
        driver.get(f"{URL_BASE}discoverychannel")
        time.sleep(20) # Tempo maior para capturar carregamento
        
        # Coleta todos os logs de performance
        logs = driver.get_log('performance')
        
        urls_capturadas = []
        for entry in logs:
            log = json.loads(entry['message'])['message']
            if log['method'] == 'Network.responseReceived':
                url = log['params']['response']['url']
                urls_capturadas.append(url)
        
        # Filtra apenas o que parece ser CSS ou JS importante
        debug_output = "\n".join([u for u in urls_capturadas if ".css" in u or "assets" in u])
        
        with open("debug_espelho.txt", "w", encoding="utf-8") as f:
            f.write(f"--- TODOS OS RECURSOS CARREGADOS (REDE) ---\n\n{debug_output}")

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
