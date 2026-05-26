import os
from playwright.sync_api import sync_playwright

def capturar_html():
    # URL alvo
    url = "https://ww2.embedtv.lat/discoverychannel"
    
    print(f"🔄 Iniciando captura via rede tunelada...")
    
    with sync_playwright() as p:
        # Iniciamos o browser sem necessidade de proxies ou stealth,
        # pois o Tailscale já está roteando o tráfego pela sua rede.
        browser = p.chromium.launch(headless=True)
        
        # Criamos um contexto com um User-Agent de navegador real
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print(f"🌐 Acessando: {url}")
            page.goto(url, timeout=30000)
            
            # Aguardamos para garantir que todo o JS foi executado
            page.wait_for_timeout(10000)
            
            # Captura o HTML para debug
            html_conteudo = page.content()
            with open("debug_espelho.txt", "w", encoding="utf-8") as f:
                f.write(html_conteudo)
            
            # Captura um screenshot para visualização
            page.screenshot(path="debug_visual.png")
            print("✅ Sucesso: HTML e screenshot salvos.")
            
        except Exception as e:
            print(f"❌ Erro durante a navegação: {e}")
        
        browser.close()

if __name__ == "__main__":
    capturar_html()
