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
    if not novo_conteudo: 
        print("⚠️ Conteúdo vazio. Atualização cancelada.")
        return
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

    novo_conteudo = "".join(linhas)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        page = context.new_page()
        
        # Bloqueador de pop-ups chatinhos da aba principal
        page.on("popup", lambda popup: popup.close())
        
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for i in range(len(linhas)):
            if '#EXTINF' in linhas[i] and 'tvg-id="' in linhas[i]:
                canal_id = re.search(r'tvg-id="([^"]+)"', linhas[i]).group(1)
                
                if "embedtv" in linhas[i+1]:
                    print(f"🔄 Checando {canal_id}...")
                    
                    url_capturada = []
                    
                    # NOVA REGRA: Pega qualquer m3u8 ou css disfarçado, independente do domínio!
                    def interceptar(response):
                        url = response.url
                        tipo = response.request.resource_type
                        
                        # Se for .m3u8 direto OU um style.css carregado pelo player (xhr/fetch)
                        if ".m3u8" in url or ("style.css" in url and tipo in ["xhr", "fetch"]):
                            url_capturada.append(url)
                    
                    context.on("response", interceptar)

                    try:
                        page.goto(f"{URL_BASE}{canal_id}", timeout=40000)
                        page.wait_for_load_state("networkidle")
                        
                        # Clica múltiplas vezes no centro para furar qualquer barreira de anúncios
                        for _ in range(3):
                            page.mouse.click(640, 360)
                            page.wait_for_timeout(1000)
                            
                        # Espera 6 segundos para dar tempo do player iniciar e puxar o vídeo da rede
                        page.wait_for_timeout(6000)
                        
                        context.remove_listener("response", interceptar)

                        if url_capturada:
                            # Pega o último link capturado (geralmente é o definitivo do vídeo)
                            nova_url = url_capturada[-1]
                            linhas[i+1] = nova_url + "\n"
                            print(f"✨ Link capturado via REDE com sucesso: {canal_id}")
                        else:
                            # Fallback buscando no HTML
                            html = page.content()
                            match = re.search(r'(https?://[^\s"\'<>]+?(?:style\.css|\.m3u8))', html, re.IGNORECASE)
                            if match:
                                linhas[i+1] = match.group(1) + "\n"
                                print(f"✨ Link capturado via HTML: {canal_id}")
                            else:
                                print(f"⚠️ Link disfarçado não gerado para {canal_id}")
                                page.screenshot(path=f"debug_{canal_id}.png")
                    
                    except Exception as e:
                        print(f"Erro em {canal_id}: {e}")
                        try:
                            context.remove_listener("response", interceptar)
                        except:
                            pass
        
        browser.close()
        novo_conteudo = "".join(linhas)
    
    with open(ARQUIVO_M3U, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    
    atualizar_repositorio(novo_conteudo)

if __name__ == "__main__":
    processar_m3u()
