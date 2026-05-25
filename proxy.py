import requests
from playwright.sync_api import sync_playwright

def get_free_proxy():
    # Busca uma lista de proxies gratuitos
    response = requests.get("https://free-proxy-list.net/")
    proxies = []
    for line in response.text.split('\n'):
        if '<tr><td>' in line:
            parts = line.split('<td>')
            ip = parts[1].replace('</td>', '')
            port = parts[2].replace('</td>', '')
            proxies.append(f"http://{ip}:{port}")
            if len(proxies) >= 5: break
    return proxies

def capturar_com_proxy():
    proxy_list = get_free_proxy()
    
    with sync_playwright() as p:
        for proxy in proxy_list:
            print(f"🔄 Tentando Proxy: {proxy}")
            try:
                browser = p.chromium.launch(headless=True, proxy={"server": proxy})
                page = browser.new_page()
                page.goto("https://ww2.embedtv.lat/", timeout=15000)
                
                # Salva o resultado
                with open("debug_proxy_final.txt", "w", encoding="utf-8") as f:
                    f.write(page.content())
                
                print("✅ Sucesso com proxy!")
                browser.close()
                return
            except Exception as e:
                print(f"❌ Proxy {proxy} falhou, tentando o próximo...")
                continue

if __name__ == "__main__":
    capturar_com_proxy()
