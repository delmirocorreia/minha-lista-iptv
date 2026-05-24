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
    # 0. Autenticação GitHub
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)

    # 1. Configurações para capturar o Network (Performance Logs)
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    
    # Ativa o registro de logs de performance
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = uc.Chrome(options=options, version_main=148)

    # 2. Acessar o canal
    canal_teste = "discoverychannel" 
    print(f"🔍 [ESPELHO] Iniciando captura de rede em: {canal_teste}")
    
    driver.get(f"{URL_BASE}{canal_teste}")
    time.sleep(20) 
    
    # 3. Extrair Logs de Rede (Network)
    logs = driver.get_log('performance')
    
    # 4. Processar os logs procurando por arquivos .css ou similar
    urls_encontradas = []
    for entry in logs:
        try:
            log_message = json.loads(entry['message'])['message']
            if log_message['method'] == 'Network.requestWillBeSent':
                url = log_message['params']['request']['url']
                urls_encontradas.append(url)
        except:
            continue

    # 5. Preparar conteúdo para o arquivo de debug
    debug_content = "--- URLS CAPTURADAS VIA NETWORK ---\n"
    debug_content += "\n".join([u for u in urls_encontradas if "css" in u or "m3u8" in u])
    debug_content += "\n\n--- LOG COMPLETO (Primeiros 100 itens) ---\n"
    debug_content += "\n".join([str(u) for u in urls_encontradas[:100]])
    
    with open("debug_espelho.txt", "w", encoding="utf-8") as f:
        f.write(debug_content)

    # 6. Enviar para o repositório
    with open("debug_espelho.txt", "r", encoding="utf-8") as f:
        conteudo = f.read()

    try:
        file_info = repo.get_contents("debug_espelho.txt")
        repo.update_file(file_info.path, "Debug: Atualizando log de rede", conteudo, file_info.sha)
        print("🚀 debug_espelho.txt atualizado!")
    except:
        repo.create_file("debug_espelho.txt", "Debug: Criando log de rede", conteudo)
        print("🚀 debug_espelho.txt criado!")
    
    driver.quit()

if __name__ == "__main__":
    processar_espelho()
