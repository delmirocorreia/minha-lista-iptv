from seleniumwire import webdriver
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

    # 1. Configurações do Navegador para Selenium Wire
    # O selenium-wire gerencia o Chrome internamente
    chrome_options = {
        'headless': True,
        'args': ['--no-sandbox', '--disable-dev-shm-usage', '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36']
    }
    
    driver = webdriver.Chrome(seleniumwire_options=chrome_options)
    
    # 2. Acessar o canal
    canal_teste = "discoverychannel" 
    print(f"🔍 [REDE] Iniciando captura de rede em: {canal_teste}")
    
    try:
        driver.get(f"{URL_BASE}{canal_teste}")
        time.sleep(20) # Tempo vital para o carregamento do CSS e da rede
        
        # 3. Captura do conteúdo do CSS via rede
        conteudo_css = "CSS NÃO ENCONTRADO"
        for request in driver.requests:
            if request.response and "style.css" in request.url:
                conteudo_css = request.response.body.decode('utf-8', errors='ignore')
                print(f"✅ CSS encontrado em: {request.url}")
                break
        
        # 4. Salvar log de auditoria
        debug_content = f"--- CONTEÚDO DO STYLE.CSS ---\n\n{conteudo_css}"
        
        with open("debug_espelho.txt", "w", encoding="utf-8") as f:
            f.write(debug_content)

        # 5. Enviar para o repositório
        with open("debug_espelho.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()

        try:
            file_info = repo.get_contents("debug_espelho.txt")
            repo.update_file(file_info.path, "Debug: Atualizando log de rede", conteudo, file_info.sha)
        except:
            repo.create_file("debug_espelho.txt", "Debug: Criando log de rede", conteudo)
            
        print("🚀 Processo concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    processar_espelho()
