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

    # Inicializa a variável no início para evitar o erro NameError se algo falhar
    novo_conteudo = "".join(linhas)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        
        # Definimos uma resolução de ecrã fixa de 1280x720 para os cliques serem exatos
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        # 🔥 TRUQUE MESTRE ANTI-POPUP: Fecha na hora qualquer aba de anúncio que o site tentar abrir
        context.on("page", lambda popup: popup.close())

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for i in range(len(linhas)):
            if '#EXTINF' in linhas[i] and 'tvg-id="' in linhas[i]:
                canal_id = re.search(r'tvg-id="([^"]+)"', linhas[i]).group(1)
                
                if "embedtv" in linhas[i+1]:
                    print(f"🔄 Checando {canal_id}...")
                    
                    url_capturada = []
                    
                    # Monitoriza a rede para pescar o falso .css assim que ele surgir
                    def interceptar(response):
                        if "style.css" in response.url and "embedtv" in response.url:
                            url_capturada.append(response.url)
                    
                    context.on("response", interceptar)

                    try:
                        page.goto(f"{URL_BASE}{canal_id}", timeout=30000)
                        page.wait_for_load_state("networkidle")
                        
                        # Clique 1: Clica no corpo da página para desarmar o anúncio invisível inicial
                        page.click("body")
                        page.wait_for_timeout(1000)
                        
                        # Clique 2: Tenta clicar no botão real, se não conseguir, clica no centro perfeito (640, 360)
                        try:
                            if page.locator(".vjs-big-play-button").is_visible():
                                page.click(".vjs-big-play-button", timeout=2000)
                            else:
                                page.mouse.click(640, 360)
                        except:
                            page.mouse.click(640, 360)
                            
                        # Aguarda 5 segundos para o player iniciar e injetar o .css disfarçado
                        page.wait_for_timeout(5000)
                        
                        context.remove_listener("response", interceptar)

                        if url_capturada:
                            nova_url = url_capturada[0]
                            linhas[i+1] = nova_url + "\n"
                            print(f"✨ Link capturado com sucesso: {canal_id}")
                        else:
                            # Alternativa caso o link já esteja exposto no código fonte
                            html = page.content()
                            match = re.search(r'(https:[^"\']*?style\.css)', html, re.IGNORECASE)
                            if match:
                                linhas[i+1] = match.group(1) + "\n"
                                print(f"✨ Link capturado (via HTML): {canal_id}")
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
