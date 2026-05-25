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
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    conteudo = repo.get_contents(ARQUIVO_M3U)
    repo.update_file(conteudo.path, "Automação: Atualizando links", novo_conteudo, conteudo.sha)

def processar_m3u():
    with open(ARQUIVO_M3U, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    links_capturados = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        for i in range(len(linhas)):
            if '#EXTINF' in linhas[i] and 'tvg-id="' in linhas[i]:
                match = re.search(r'tvg-id="([^"]+)"', linhas[i])
                if not match: continue
                
                canal_id = match.group(1)
                print(f"🔄 Processando: {canal_id}")

                # Cria um contexto novo para cada canal (limpa cookies/cache)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # Variável para armazenar o link deste canal
                url_encontrada = None

                def handle_response(response):
                    nonlocal url_encontrada
                    if "style.css" in response.url:
                        url_encontrada = response.url

                page.on("response", handle_response)

                try:
                    page.goto(f"{URL_BASE}{canal_id}", wait_until="networkidle", timeout=60000)
                    page.wait_for_timeout(5000) # Tempo extra para carregar recursos dinâmicos
                    
                    if url_encontrada:
                        links_capturados[canal_id] = url_encontrada
                        print(f"✅ Sucesso: {url_encontrada}")
                    else:
                        print(f"⚠️ CSS não encontrado para {canal_id}")
                
                except Exception as e:
                    print(f"Erro ao processar {canal_id}: {e}")

                page.close()
                context.close()

        browser.close()

    # Atualiza a lista na memória
    novo_conteudo_lista = []
    for linha in linhas:
        novo_conteudo_lista.append(linha)
        if '#EXTINF' in linha and 'tvg-id="' in linha:
            match = re.search(r'tvg-id="([^"]+)"', linha)
            if match:
                canal_id = match.group(1)
                if canal_id in links_capturados:
                    # Substitui a linha seguinte (a URL) pelo link novo
                    # Removemos a linha original e colocamos a nova
                    novo_conteudo_lista.pop() 
                    novo_conteudo_lista.append(linha)
                    novo_conteudo_lista.append(links_capturados[canal_id] + "\n")

    # Envia para o GitHub
    atualizar_repositorio("".join(novo_conteudo_lista))
    print("\n🚀 Fim do processo. Repositório atualizado.")

if __name__ == "__main__":
    processar_m3u()
