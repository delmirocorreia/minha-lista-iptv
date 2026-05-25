import os
from playwright.sync_api import sync_playwright
import playwright_stealth

# --- CONFIGURAÇÕES ---
URL_TESTE = "https://ww2.embedtv.lat/discoverychannel" 

def capturar_html_stealth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Acesso direto ao módulo importado como "playwright_stealth"
        # O método correto na maioria das versões é acessar o atributo "stealth"
        try:
            playwright_stealth.stealth(page)
            print("✅ Stealth aplicado com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao aplicar stealth: {e}")
            # Se falhar, tentamos a forma alternativa de alguns pacotes
            try:
                playwright_stealth.stealth_sync(page)
                print("✅ Stealth aplicado via stealth_sync!")
            except:
                print("❌ Não foi possível aplicar stealth, continuando sem...")

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
