import re
import os
from playwright.sync_api import sync_playwright, TimeoutError
from github import Github, Auth

ARQUIVO_M3U = "index.m3u"
URL_BASE = "https://ww2.embedtv.lat/"
REPO_NAME = "delmirocorreia/minha-lista-iptv"
GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")


def atualizar_repositorio(novo_conteudo):
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    repo = g.get_repo(REPO_NAME)

    conteudo = repo.get_contents(ARQUIVO_M3U)

    repo.update_file(
        conteudo.path,
        "Automação: Atualizando links",
        novo_conteudo,
        conteudo.sha
    )


def processar_m3u():

    with open(ARQUIVO_M3U, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--autoplay-policy=no-user-gesture-required",
                "--mute-audio",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/136.0.0.0 "
                "Safari/537.36"
            ),
            viewport={
                "width": 1366,
                "height": 768
            }
        )

        page = context.new_page()

        links_capturados = {}

        canal_contexto = {
            "id": None
        }

        # =========================
        # DEBUG DE REQUESTS
        # =========================

        def handle_request(request):
            print(f"➡ REQUEST: {request.url}")

        context.on("request", handle_request)

        # =========================
        # CAPTURA DE RESPONSES
        # =========================

        def handle_response(response):

            url = response.url

            print(f"⬅ RESPONSE: {url}")

            # FILTRO PRINCIPAL
            if "style.css" in url:

                canal = canal_contexto["id"]

                if canal and canal not in links_capturados:

                    print(f"\n✅ LINK CAPTURADO")
                    print(f"📺 Canal: {canal}")
                    print(f"🔗 URL: {url}\n")

                    links_capturados[canal] = url

        context.on("response", handle_response)

        # =========================
        # LOOP DOS CANAIS
        # =========================

        for i in range(len(linhas)):

            if '#EXTINF' in linhas[i] and 'tvg-id="' in linhas[i]:

                match = re.search(
                    r'tvg-id="([^"]+)"',
                    linhas[i]
                )

                if not match:
                    continue

                canal_id = match.group(1)

                canal_contexto["id"] = canal_id

                print("\n===================================")
                print(f"🔄 PROCESSANDO: {canal_id}")
                print("===================================\n")

                try:

                    url_canal = f"{URL_BASE}{canal_id}"

                    page.goto(
                        url_canal,
                        wait_until="networkidle",
                        timeout=60000
                    )

                    print("✅ Página carregada")

                    # =========================
                    # DEBUG
                    # =========================

                    page.screenshot(
                        path=f"debug_{canal_id}.png"
                    )

                    with open(
                        f"debug_{canal_id}.html",
                        "w",
                        encoding="utf-8"
                    ) as f:
                        f.write(page.content())

                    # =========================
                    # LISTAR IFRAMES
                    # =========================

                    print("\n🖼 IFRAMES ENCONTRADOS:")

                    for frame in page.frames:
                        print("FRAME:", frame.url)

                    print()

                    # =========================
                    # TENTATIVAS DE INTERAÇÃO
                    # =========================

                    try:

                        # Clique central
                        page.mouse.click(500, 300)

                        print("▶ Clique enviado no player")

                    except Exception as e:
                        print("❌ Erro ao clicar:", e)

                    # Espera pós clique
                    page.wait_for_timeout(8000)

                    # =========================
                    # ESPERA EXPLÍCITA
                    # =========================

                    try:

                        response = page.wait_for_response(
                            lambda r: "style.css" in r.url,
                            timeout=15000
                        )

                        print("\n🎯 STYLE.CSS ENCONTRADO:")
                        print(response.url)

                    except TimeoutError:

                        print(
                            "⚠ style.css não encontrado "
                            "dentro do timeout"
                        )

                except Exception as e:

                    print(f"❌ ERRO NO CANAL {canal_id}")
                    print(str(e))

        browser.close()

    # =========================
    # ATUALIZAÇÃO DO M3U
    # =========================

    for i in range(len(linhas)):

        if '#EXTINF' in linhas[i]:

            match = re.search(
                r'tvg-id="([^"]+)"',
                linhas[i]
            )

            if not match:
                continue

            canal_id = match.group(1)

            if canal_id in links_capturados:

                linhas[i + 1] = (
                    links_capturados[canal_id] + "\n"
                )

                print(f"✅ Atualizado no M3U: {canal_id}")

    # =========================
    # ENVIO PARA GITHUB
    # =========================

    novo_conteudo = "".join(linhas)

    atualizar_repositorio(novo_conteudo)

    print("\n🚀 Repositório atualizado com sucesso!")


if __name__ == "__main__":
    processar_m3u()
