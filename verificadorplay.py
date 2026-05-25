import re
import os
from playwright.sync_api import sync_playwright
from github import Github, Auth

# --- CONFIGURAÇÕES ---
ARQUIVO_M3U = "index.m3u"
URL_BASE = "https://ww2.embedtv.lat/"
REPO_NAME = "delmirocorreia/minha-lista-iptv"
GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")

def atualizar_repositorio(novo_conteudo):
    try:
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
        print("🚀 Repositório atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar GitHub: {e}")

def processar_m3u():
    with open(ARQUIVO_M3U, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    with sync_playwright() as p:
        # Lançamento do navegador com argumentos anti-bot
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        # Esconde que é um robô do Playwright
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for i in range(len(linhas)):
            if '#EXTINF' in linhas[i] and 'tvg-id="' in linhas[i]:
                canal_id = re.search(r'tvg-id="([^"]+)"', linhas[i]).group(1)
                url_antiga = linhas[i+1].strip()

                if "embedtv" in url_antiga:
                    print(f"🔄 Checando {canal_id}...")
                    try:
                        page.goto(f"{URL_BASE}{canal_id}")
                        page.wait_for_load_state("networkidle")
                        
                        try:
                            page.click('.vjs-big-play-button', timeout=5000)
                            page.wait_for_timeout(3000)
                        except:
                            pass

                        html = page.content()
                        match = re.search(r'(https:[^"\']*?style\.css)', html, re.IGNORECASE)
                        
                        if match:
                            url_nova = match.group(1)
                            if url_nova != url_antiga:
                                print(f"✨ Atualizado: {canal_id}")
                                linhas[i+1] = url_nova + "\n"
                            else:
                                print(f"✅ {canal_id} ok.")
                        else:
                            print(f"⚠️ Link não encontrado para {canal_id}")
                            page.screenshot(path=f"debug_{canal_id}.png")
                    except Exception as e:
                        print(f"Erro: {e}")
        
        browser.close()
    
    novo_conteudo = "".join(linhas)
    with open(ARQUIVO_M3U, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    
    atualizar_repositorio(novo_conteudo)

if __name__ == "__main__":
    processar_m3u()
    
    atualizar_repositorio(novo_conteudo)

if __name__ == "__main__":
    processar_m3u()
