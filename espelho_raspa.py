import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# --- CONFIGURAÇÕES ---
URL_TESTE = "https://ww2.embedtv.lat/discoverychannel" 

def capturar_html_stealth():
    with sync_playwright() as p:
        # Lança o navegador
        browser = p.chromium.launch(headless=True)
        # Cria um contexto com User-Agent fixo
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Aplica a camuflagem stealth
        stealth_sync(page)

        print(f"🔄 Acessando com Stealth: {URL_TESTE}")
        
        try:
            page.goto(URL_TESTE)
            page.wait_for_timeout(10000) # Tempo para renderização JS

            # Salva o HTML no arquivo debug_espelho.txt
            html_conteudo = page.content()
            with open("debug_espelho.txt", "w", encoding="utf-8") as f:
                f.write(html_conteudo)
            
            # Screenshot para inspeção visual
            page.screenshot(path="debug_visual.png")
            print("✅ Sucesso: HTML e Screenshot salvos.")
            
        except Exception as e:
            print(f"❌ Erro durante a execução: {e}")
            
        browser.close()

if __name__ == "__main__":
    capturar_html_stealth()
