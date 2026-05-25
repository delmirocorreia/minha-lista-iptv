import os
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÕES ---
# Coloque aqui a URL completa de um canal que você sabe que tem o link
URL_TESTE = "https://ww2.embedtv.lat/discoverychannel" 

def capturar_html_bruto():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Contexto com User-Agent real
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"🔄 Acessando: {URL_TESTE}")
        page.goto(URL_TESTE)
        
        # Espera o carregamento completo do JS
        page.wait_for_timeout(10000) 

        # Captura o HTML "Ctrl+U"
        html_conteudo = page.content()

        # Salva exatamente no arquivo que você solicitou
        nome_arquivo = "debug_espelho.txt"
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(html_conteudo)
        
        print(f"✅ HTML salvo em {nome_arquivo}")
        
        # Opcional: Screenshot para ver se há bloqueio visual
        page.screenshot(path="debug_visual.png")
        
        browser.close()

if __name__ == "__main__":
    capturar_html_bruto()
