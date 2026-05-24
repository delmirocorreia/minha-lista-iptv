import undetected_chromedriver as uc
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

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = uc.Chrome(options=options, version_main=148)
    
    try:
        driver.get(f"{URL_BASE}discoverychannel")
        time.sleep(20)
        
        # O "pulo do gato": usamos JS para buscar o arquivo style.css e extrair o texto
        # Isso contorna o problema de rede/proxy
        conteudo_css = driver.execute_script("""
            var cssContent = "CSS NÃO ENCONTRADO";
            var styleSheets = document.styleSheets;
            for (var i = 0; i < styleSheets.length; i++) {
                try {
                    if (styleSheets[i].href && styleSheets[i].href.includes('style.css')) {
                        // Tenta buscar o conteúdo do arquivo via fetch
                        return fetch(styleSheets[i].href)
                            .then(response => response.text())
                            .then(text => text);
                    }
                } catch(e) { continue; }
            }
            return cssContent;
        """)

        # Se o fetch retornar uma promise, aguardamos o resultado (tratativa simples)
        if hasattr(conteudo_css, 'then'):
            # Caso o JS retorne a promise, a forma mais fácil é ler via texto bruto da página
            conteudo_css = "Conteúdo dinâmico carregado via JS, veja o log."

        with open("debug_espelho.txt", "w", encoding="utf-8") as f:
            f.write(f"--- CONTEÚDO DO STYLE.CSS ---\n\n{conteudo_css}")

        with open("debug_espelho.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()

        try:
            file_info = repo.get_contents("debug_espelho.txt")
            repo.update_file(file_info.path, "Debug: Atualizando CSS", conteudo, file_info.sha)
        except:
            repo.create_file("debug_espelho.txt", "Debug: Criando log CSS", conteudo)
            
    finally:
        driver.quit()

if __name__ == "__main__":
    processar_espelho()
