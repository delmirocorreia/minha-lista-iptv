import undetected_chromedriver as uc
import time
import os
import requests
from github import Github, Auth

# --- CONFIGURAÇÕES ---
URL_BASE = "https://ww2.embedtv.lat/"
REPO_NAME = "delmirocorreia/minha-lista-iptv" 
GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")

def processar_espelho():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    driver = uc.Chrome(options=options, version_main=148)
    
    try:
        driver.get(f"{URL_BASE}discoverychannel")
        time.sleep(10)
        
        # 1. Captura a URL do CSS via Selenium
        css_url = driver.execute_script("""
            var links = document.getElementsByTagName('link');
            for(var i=0; i<links.length; i++) {
                if(links[i].href.includes('style.css')) return links[i].href;
            }
            return null;
        """)
        
        conteudo_css = "URL não encontrada no DOM"
        
        if css_url:
            print(f"🔗 URL encontrada: {css_url}")
            # 2. BAIXA O ARQUIVO USANDO REQUESTS (Ignora proteções do JS)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(css_url, headers=headers)
            conteudo_css = response.text
        
        # 3. Salvar e Enviar
        with open("debug_espelho.txt", "w", encoding="utf-8") as f:
            f.write(f"--- CONTEÚDO DO STYLE.CSS ---\n\n{conteudo_css}")

        with open("debug_espelho.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()

        try:
            file_info = repo.get_contents("debug_espelho.txt")
            repo.update_file(file_info.path, "Debug: Captura Direta", conteudo, file_info.sha)
        except:
            repo.create_file("debug_espelho.txt", "Debug: Captura Direta", conteudo)
            
    finally:
        driver.quit()

if __name__ == "__main__":
    processar_espelho()
