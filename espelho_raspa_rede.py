import undetected_chromedriver as uc
import time
import os
from github import Github, Auth

# --- CONFIGURAÇÕES ---
URL_BASE = "https://ww2.embedtv.lat/"
REPO_NAME = "delmirocorreia/minha-lista-iptv" 
GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")

def processar_espelho():
    # 0. Autenticação GitHub
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)

    # 1. Configurações do Navegador (Fingimento Total)
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    
    # Inicializa forçando a versão 148 do Chrome (ambiente do GitHub Actions)
    driver = uc.Chrome(options=options, version_main=148)

    # 2. Acessar o canal de teste
    canal_teste = "discoverychannel" 
    print(f"🔍 [ESPELHO] Iniciando teste em: {canal_teste}")
    
    driver.get(f"{URL_BASE}{canal_teste}")
    
    # 3. Espera "Paciente" (o site precisa de tempo para o JS carregar)
    time.sleep(20) 
    
    # 4. Captura o HTML com JavaScript (mais preciso que page_source)
    html_final = driver.execute_script("return document.documentElement.outerHTML;")
    
    # 5. Salvar localmente no servidor temporário
    with open("debug_espelho.txt", "w", encoding="utf-8") as f:
        f.write(html_final)

    # 6. Enviar para o repositório (Git Upload)
    with open("debug_espelho.txt", "r", encoding="utf-8") as f:
        conteudo = f.read()

    try:
        # Tenta atualizar se já existir
        file_info = repo.get_contents("debug_espelho.txt")
        repo.update_file(file_info.path, "Debug: Atualizando log de auditoria", conteudo, file_info.sha)
        print("🚀 debug_espelho.txt atualizado com sucesso!")
    except:
        # Cria se não existir
        repo.create_file("debug_espelho.txt", "Debug: Criando log de auditoria", conteudo)
        print("🚀 debug_espelho.txt criado com sucesso!")
    
    driver.quit()

if __name__ == "__main__":
    processar_espelho()
