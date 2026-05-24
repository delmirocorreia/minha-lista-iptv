import undetected_chromedriver as uc
import time
import os
from github import Github, Auth

# --- CONFIGURAÇÕES ---
URL_BASE = "https://ww2.embedtv.lat/"
REPO_NAME = "delmirocorreia/minha-lista-iptv" 
GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")

def processar_espelho():
    # 0. Inicializar autenticação do GitHub
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)

    # 1. Configurações do Navegador
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    
    driver = uc.Chrome(options=options, version_main=148)

    # 2. Teste
    canal_teste = "discoverychannel" 
    print(f"🔍 [ESPELHO] Iniciando teste em: {canal_teste}")
    
    driver.get(f"{URL_BASE}{canal_teste}")
    time.sleep(15) 
    
    # 4. Captura bruta
    html_final = driver.page_source
    
    # 5. Salvar localmente
    with open("debug_espelho.txt", "w", encoding="utf-8") as f:
        f.write(html_final)

    # 6. Enviar para o GitHub
    with open("debug_espelho.txt", "r", encoding="utf-8") as f:
        conteudo = f.read()

    try:
        file_info = repo.get_contents("debug_espelho.txt")
        repo.update_file(file_info.path, "Debug: Atualizando log", conteudo, file_info.sha)
        print("🚀 debug_espelho.txt atualizado!")
    except:
        repo.create_file("debug_espelho.txt", "Debug: Criando log", conteudo)
        print("🚀 debug_espelho.txt criado!")
    
    driver.quit()

if __name__ == "__main__":
    processar_espelho()
