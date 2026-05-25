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
    if not novo_conteudo: return
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

    novo_conteudo = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for i in range(len(linhas)):
            if '#EXTINF' in linhas[i] and 'tvg-id="' in linhas[i]:
                canal_id = re.search(r'tvg-id="([^"]+)"', linhas[i]).group(1)
                
                if "embedtv" in linhas[i+1]:
                    print(f"🔄 Checando {canal_id}...")
                    
                    # Variável para guardar a URL capturada pela rede
                    url_capturada = []
                    
                    # Função que escuta o tráfego (igual a aba Network do navegador)
                    def interceptar(response):
                        if "style.css" in response.url and "embedtv" in response.url:
                            url_capturada.append(response.url)
                    
                    page.on("response", interceptar)

                    try:
                        page.goto(f"{URL_BASE}{canal_id}")
                        page.wait_for_load_state("networkidle")
                        
                        # O SEGREDO DO SEU VÍDEO: Clicar DUAS vezes para burlar o pop-up
                        page.mouse.click(500, 300) # Clique 1: Absorvido pelo anúncio
                        page.wait_for_timeout(1500)
                        page.mouse.click(500, 300) # Clique 2: Dá play no vídeo de verdade
                        page.wait_for_timeout(4000) # Espera 4 segundos para o vídeo rodar e o css carregar
                        
                        # Removemos o "olheiro" da rede para não misturar com o próximo canal
                        page.remove_listener("response", interceptar)

                        # Verifica se o link foi capturado na rede
                        if url_capturada:
                            nova_url = url_capturada[0]
                            linhas[i+1] = nova_url + "\n"
                            print(f"✨ Atualizado com sucesso: {canal_id}")
                        else:
                            # Fallback de segurança: busca no HTML caso a rede falhe
                            html = page.content()
                            match = re.search(r'(https:[^"\']*?style\.css)', html, re.IGNORECASE)
                            if match:
                                linhas[i+1] = match.group(1) + "\n"
                                print(f"✨ Atualizado (via HTML): {canal_id}")
                            else:
                                print(f"⚠️ Link não encontrado para {canal_id}")
                                page.screenshot(path=f"debug_{canal_id}.png")
                    
                    except Exception as e:
                        print(f"Erro em {canal_id}: {e}")
                        page.remove_listener("response", interceptar) # Limpa em caso de erro
        
        browser.close()
        novo_conteudo = "".join(linhas)
    
    with open(ARQUIVO_M3U, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    
    atualizar_repositorio(novo_conteudo)

if __name__ == "__main__":
    processar_m3u()
