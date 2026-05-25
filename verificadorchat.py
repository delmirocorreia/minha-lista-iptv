import re
import os
from playwright.sync_api import sync_playwright
from github import Github, Auth

# =========================
# CONFIGURAÇÕES
# =========================

ARQUIVO_M3U = "index.m3u"

URL_BASE = "https://ww2.embedtv.lat/"

REPO_NAME = "delmirocorreia/minha-lista-iptv"

GITHUB_TOKEN = os.getenv("MEU_TOKEN_GITHUB")


# =========================
# GITHUB
# =========================

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


# =========================
# PROCESSAMENTO
# =========================

def processar_m3u():

    with open(
        ARQUIVO_M3U,
        "r",
        encoding="utf-8"
    ) as f:

        linhas = f.readlines()

    links_capturados = {}

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-blink-features=AutomationControlled",
                "--mute-audio"
            ]
        )

        # =========================
        # LOOP DOS CANAIS
        # =========================

        for i in range(len(linhas)):

            if '#EXTINF' not in linhas[i]:
                continue

            if 'tvg-id="' not in linhas[i]:
                continue

            match = re.search(
                r'tvg-id="([^"]+)"',
                linhas[i]
            )

            if not match:
                continue

            canal_id = match.group(1)

            print("\n===================================")
            print(f"🔄 PROCESSANDO: {canal_id}")
            print("===================================\n")

            # =========================
            # CONTEXTO LIMPO
            # =========================

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

            # =========================
            # BLOQUEADOR DE ADS
            # =========================

            def bloquear_ads(route):

                url = route.request.url

                ads = [
                    "doubleclick",
                    "googlesyndication",
                    "spin83qr",
                    "profferstrack",
                    "ultraplusadblocker",
                    "adexchangerapid",
                    "acscdn"
                ]

                if any(ad in url for ad in ads):

                    print(f"🚫 BLOQUEADO: {url}")

                    route.abort()

                else:

                    route.continue_()

            context.route("**/*", bloquear_ads)

            page = context.new_page()

            # =========================
            # URL FINAL
            # =========================

            url_encontrada = None

            # =========================
            # REQUESTS
            # =========================

            def handle_request(request):

                nonlocal url_encontrada

                url = request.url

                print(f"➡ REQUEST: {url}")

                # =========================
                # STYLE.CSS REAL
                # =========================

                if (
                    "cloudflaire.lat" in url
                    and "style.css" in url
                ):

                    if not url_encontrada:

                        url_encontrada = url

                        print("\n🔥 STYLE REAL ENCONTRADO (REQUEST)")
                        print(url)

            context.on(
                "request",
                handle_request
            )

            # =========================
            # RESPONSES
            # =========================

            def handle_response(response):

                nonlocal url_encontrada

                url = response.url

                print(f"⬅ RESPONSE: {url}")

                # =========================
                # STYLE.CSS REAL
                # =========================

                if (
                    "cloudflaire.lat" in url
                    and "style.css" in url
                ):

                    if not url_encontrada:

                        url_encontrada = url

                        print("\n🔥 STYLE REAL ENCONTRADO (RESPONSE)")
                        print(url)

            context.on(
                "response",
                handle_response
            )

            # =========================
            # PROCESSAMENTO
            # =========================

            try:

                url_canal = (
                    f"{URL_BASE}{canal_id}"
                )

                page.goto(
                    url_canal,
                    wait_until="networkidle",
                    timeout=60000
                )

                print("✅ Página carregada")

                # =========================
                # SCREENSHOT
                # =========================

                page.screenshot(
                    path=f"debug_{canal_id}.png"
                )

                # =========================
                # HTML
                # =========================

                with open(
                    f"debug_{canal_id}.html",
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(page.content())

                # =========================
                # IFRAMES
                # =========================

                print("\n🖼 IFRAMES:")

                for frame in page.frames:

                    print(frame.url)

                print()

                # =========================
                # ESPERA INICIAL
                # =========================

                page.wait_for_timeout(5000)

                # =========================
                # CLIQUES
                # =========================

                for tentativa in range(5):

                    print(
                        f"\n▶ Tentativa "
                        f"{tentativa + 1}"
                    )

                    try:

                        # Clique REAL DOM
                        page.click(
                            "body",
                            timeout=5000
                        )

                    except Exception as e:

                        print(
                            "❌ Erro clique:",
                            e
                        )

                    # =========================
                    # ESPERA LONGA
                    # =========================

                    page.wait_for_timeout(15000)

                    # =========================
                    # SE ENCONTROU
                    # =========================

                    if url_encontrada:

                        break

                # =========================
                # RESULTADO
                # =========================

                if url_encontrada:

                    links_capturados[
                        canal_id
                    ] = url_encontrada

                    print(
                        "\n✅ STYLE.CSS "
                        "CAPTURADO"
                    )

                    print(url_encontrada)

                else:

                    print(
                        "\n⚠ STYLE.CSS "
                        "NÃO ENCONTRADO"
                    )

            except Exception as e:

                print(
                    f"\n❌ ERRO EM "
                    f"{canal_id}"
                )

                print(str(e))

            finally:

                page.close()

                context.close()

        browser.close()

    # =========================
    # ATUALIZA M3U
    # =========================

    for i in range(len(linhas)):

        if '#EXTINF' not in linhas[i]:
            continue

        match = re.search(
            r'tvg-id="([^"]+)"',
            linhas[i]
        )

        if not match:
            continue

        canal_id = match.group(1)

        if canal_id in links_capturados:

            linhas[i + 1] = (
                links_capturados[canal_id]
                + "\n"
            )

            print(
                f"✅ Atualizado: "
                f"{canal_id}"
            )

    # =========================
    # ENVIA GITHUB
    # =========================

    novo_conteudo = "".join(linhas)

    atualizar_repositorio(
        novo_conteudo
    )

    print(
        "\n🚀 PROCESSO FINALIZADO"
    )


# =========================
# START
# =========================

if __name__ == "__main__":

    processar_m3u()
