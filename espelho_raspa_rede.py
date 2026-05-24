import undetected_chromedriver as uc
import time
import os
import requests
import re
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
        time.sleep(15)
        
        # Captura o HTML bruto de toda a página
        html_page = driver.page_source
        
        # Usa Regex para encontrar qualquer link que termine em .css
        # Isso busca URLs dentro de scripts, tags de style, etc.
        urls_css = re.findall(r'https?://[^\s<>"]+\.css', html_page)
        
        conteudo_final = "Nenhuma URL de CSS encontrada no HTML bruto."
        
        if urls_css:
            # Pega a primeira URL que encontrar
            css_url = urls_css[0]
            print(f"🔗 URL encontrada via Regex: {css_url}")
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(css_url, headers=headers)
            conteudo_final = f"--- URL: {css_url} ---\n\n{response.text}"
        
        # Salvar o log
        with open("debug_espelho.txt", "w", encoding="utf-8") as f:
            f.write(conteudo_final)

        with open("debug_espelho.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()

        try:
            file_info = repo.get_contents("debug_espelho.txt")
            repo.update_file(file_info.path, "Debug: Captura Regex [skip ci]", conteudo, file_info.sha)
        except:
            repo.create_file("debug_espelho.txt", "Debug: Captura Regex [skip ci]", conteudo)
            
    finally:
        driver.quit()

if __name__ == "__main__":
    processar_espelho()
