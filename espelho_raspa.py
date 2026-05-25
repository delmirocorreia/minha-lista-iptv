import os
from playwright.sync_api import sync_playwright
import playwright_stealth

# --- CONFIGURAÇÕES ---
URL_TESTE = "https://ww2.embedtv.lat/" 

def capturar_html_stealth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Aplicação segura do Stealth
        try:
            # Tenta acessar o atributo 'stealth' dentro do módulo
            if hasattr(playwright_stealth, 'stealth'):
                playwright_stealth.stealth(page)
                print("✅ Stealth aplicado via stealth()")
            else:
                # Fallback para versões onde a função se chama 'stealth_sync'
                playwright_stealth.stealth_sync(page)
                print("✅ Stealth aplicado via stealth_sync()")
        except Exception as e:
            print(f"⚠️ Erro ao aplicar stealth: {e}")

        print(f"🔄 Acessando: {URL_TESTE}")
        
        try:
            page.goto(URL_TESTE)
            page.wait_for_timeout(10000) 

            # Salva o conteúdo
            html_conteudo = page.content()
            with open("debug_espelho.txt", "w", encoding="utf-8") as f:
                f.write(html_conteudo)
            
            page.screenshot(path="debug_visual.png")
            print("✅ Sucesso: Arquivos de debug criados.")
        except Exception as e:
            print(f"❌ Erro na navegação: {e}")
            
        browser.close()

if __name__ == "__main__":
    capturar_html_stealth()
