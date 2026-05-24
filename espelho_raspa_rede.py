import undetected_chromedriver as uc
from seleniumwire import webdriver # Usaremos a versão que intercepta a rede
import time
import os
from github import Github, Auth

# --- CONFIGURAÇÕES ---
URL_BASE = "https://ww2.embedtv.lat/"
REPO_NAME = "delmirocorreia/minha-lista-iptv" 
GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")

def processar_espelho():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)

    # Configurações do Selenium Wire
    options = {
        'headless': True,
        'args': ['--no-sandbox', '--disable-dev-shm-usage']
    }
    
    # Inicializa o driver com suporte a interceptação de rede
    driver = webdriver.Chrome(seleniumwire_options=options, version_main=148)
    
    driver.get(f"{URL_BASE}discoverychannel")
    time.sleep(20) # Tempo para garantir o carregamento do CSS
    
    conteudo_css = "CSS NÃO ENCONTRADO"
    
    # Procura em todas as requisições feitas pelo navegador
    for request in driver.requests:
        if request.response and "style.css" in request.url:
            # Captura o texto de dentro do arquivo CSS
            conteudo_css = request.response.body.decode('utf-8')
            print(f"✅ CSS capturado de: {request.url}")
            break
            
    # Salva o conteúdo do CSS no arquivo de debug
    with open("debug_espelho.txt", "w", encoding="utf-8") as f:
        f.write(f"--- CONTEÚDO DO STYLE.CSS ---\n\n{conteudo_css}")

    # Envio para o GitHub (mesma lógica anterior)
    with open("debug_espelho.txt", "r", encoding="utf-8") as f:
        conteudo = f.read()

    try:
        file_info = repo.get_contents("debug_espelho.txt")
        repo.update_file(file_info.path, "Debug: Atualizando CSS", conteudo, file_info.sha)
    except:
        repo.create_file("debug_espelho.txt", "Debug: Criando log de CSS", conteudo)
    
    driver.quit()

if __name__ == "__main__":
    processar_espelho()
