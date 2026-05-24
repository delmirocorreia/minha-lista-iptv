import undetected_chromedriver as uc
import time
import os
from github import Github, Auth

# --- CONFIGURAÇÕES ---
ARQUIVO_M3U = "index.m3u"
URL_BASE = "https://ww2.embedtv.lat/"
# ... resto das configs iguais ...

def processar_espelho():
    # 1. Configurações de "Fingimento" Total
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    
    driver = uc.Chrome(options=options)

    # 2. Testar apenas 1 canal para não gastar tempo de Actions
    canal_teste = "discoverychannel" 
    print(f"🔍 [ESPELHO] Iniciando teste em: {canal_teste}")
    
    driver.get(f"{URL_BASE}{canal_teste}")
    
    # 3. Espera "Paciente" (Humana)
    time.sleep(15) 
    
    # 4. Captura bruta do que o navegador renderizou após o JS
    html_final = driver.page_source
    
    # 5. Salvar o log de auditoria no repositório
    with open("debug_espelho.txt", "w", encoding="utf-8") as f:
        f.write(html_final)
    
    print("✅ Raspagem concluída. Verifique o arquivo debug_espelho.txt no repositório.")
    driver.quit()

if __name__ == "__main__":
    processar_espelho()