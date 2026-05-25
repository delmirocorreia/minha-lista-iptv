import os
from playwright.sync_api import sync_playwright
# Importando explicitamente o objeto stealth
from playwright_stealth import stealth

# --- CONFIGURAÇÕES ---
URL_TESTE = "https://ww2.embedtv.lat/discoverychannel" 

def capturar_html_stealth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # O erro anterior ocorria porque o Python estava tentando chamar o módulo como função.
        # Ao usar o "stealth" importado, estamos chamando a função dentro do módulo.
        try:
            # Caso o import acima ainda dê erro de módulo, usamos a função oculta:
            from playwright_stealth import stealth_sync
            stealth_sync(page)
            print("✅ Stealth aplicado via stealth_sync")
        except:
            # Fallback para o caso de a estrutura de diretórios mudar
            import playwright_stealth
            playwright_stealth.stealth(page)
            print("✅ Stealth aplicado via fallback")

        print(f"🔄 Acessando: {URL_TESTE}")
        
        try:
            page.goto(URL_TESTE)
            page.wait_for_timeout(10000) 

            html_conteudo = page.content()
            with open("debug_espelho.txt", "w", encoding="utf-8") as f:
                f.write(html_conteudo)
            
            page.screenshot(path="debug_visual.png")
            print("✅ Sucesso: Arquivos salvos.")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            
        browser.close()

if __name__ == "__main__":
    capturar_html_stealth()
