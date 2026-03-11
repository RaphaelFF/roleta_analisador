from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import time

load_dotenv()

URL_SITE = os.getenv('URL_SITE')
URL_ROLETA_BASE = os.getenv('URL_ROLETA_BASE')
USER = os.getenv('USER')
PASS = os.getenv('PASS')

def executar_bot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            geolocation={"longitude": -46.6333, "latitude": -23.5505}, # São Paulo
            permissions=["geolocation"]
        )
        
        # Mascarar automação
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        context.set_default_timeout(60000)
        page = context.new_page()

        try:
            # 2. ACESSO E COOKIES
            print("Acessando Superbet...")
            page.goto(URL_SITE, wait_until="domcontentloaded", timeout=90000)
            
            try:
                page.locator("#onetrust-accept-btn-handler").click(timeout=15000)
                print("Cookies aceitos.")
            except: pass

            # 3. LOGIN
            print("Realizando login...")
            page.wait_for_selector("button.e2e-login", state="visible")
            page.click("button.e2e-login")
            page.fill('input[name="username"]', USER)
            page.fill('input[name="password"]', PASS)
            page.click("#login-modal-submit")
            
            # Aguarda a área logada estabilizar
            page.wait_for_selector(".header__right", timeout=40000)
            print("Login confirmado.")
            time.sleep(3)

            # 4. CAPTURAR LINK DO JOGO (IFRAME)
            print("Indo para a página da roleta...")
            page.goto(URL_ROLETA_BASE, wait_until="domcontentloaded", timeout=90000)
            
            print("Extraindo link direto do jogo dentro do iframe...")
            page.wait_for_selector("iframe.iframe", state="attached", timeout=60000)
            link_direto = page.get_attribute("iframe.iframe", "src")
            
            if not link_direto:
                raise Exception("Não foi possível extrair o link 'src' do iframe.")

            # 5. NAVEGAÇÃO DIRETA (BYPASS)
            print("Navegando diretamente para o motor do jogo (Pragmatic)...")
            page.goto(link_direto, wait_until="domcontentloaded", timeout=90000)
            
            # Espera o motor gráfico inicializar
            print("Aguardando inicialização do jogo...")
            time.sleep(15) 

            # 6. ABRIR ESTATÍSTICAS
            print("Buscando botão de estatísticas...")
            
            # Usando o seletor que funcionou anteriormente
            btn_stats = page.locator('button:has(svg[data-testid="icon-Statistics"]), button[data-testid="icon-Statistics"]').first
            btn_stats.wait_for(state="visible", timeout=60000)
            btn_stats.click()
            print("Menu de estatísticas aberto.")
            time.sleep(2)

            # 7. FILTRAR ÚLTIMOS 500 (O passo que faltava)
            print("Clicando em 'Últimos 500'...")
            btn_500 = page.locator('button[data-tab-key="last500"]').first
            btn_500.wait_for(state="visible", timeout=20000)
            btn_500.click()
            print("Filtro de 500 números ativado.")
            time.sleep(2)

            print("\n--- MONITORAMENTO ATIVO (ANTI-INATIVIDADE ATIVADO) ---")
            
            ultimo_historico_completo = []
            ultimo_clique_atividade = time.time()

            while True:
                '''
                try:
                    # 1. LÓGICA ANTI-INATIVIDADE (Alternando Abas)
                    agora = time.time()
                    if agora - ultimo_clique_atividade > 120:  # A cada 2 minutos
                        try:
                            print(f"[{time.strftime('%H:%M:%S')}] Resetando timer de inatividade...")
                            
                            # Clica na aba "Gráficos"
                            btn_charts = page.locator('button[data-tab-key="charts"]')
                            if btn_charts.is_visible():
                                btn_charts.click(force=True)
                                time.sleep(1) # Pequena pausa para o sistema processar a troca
                                
                                # Volta para a aba "Últimos 500"
                                btn_500 = page.locator('button[data-tab-key="last500"]')
                                btn_500.click(force=True)
                                
                                ultimo_clique_atividade = agora
                                print("✅ Interação via abas concluída com sucesso.")
                        except Exception as e:
                            print(f"⚠️ Erro ao alternar abas: {e}")
                '''    

                # 2. CAPTURA DE NÚMEROS (INCLUINDO REPETIDOS)
                container = page.locator('div[data-testid="game-statistics"]')
                # Pegamos a lista de todos os últimos números visíveis
                numeros_atuais = container.locator('div[data-testid="single-result"]').all_inner_texts()
                
                if numeros_atuais:
                    # Se o histórico mudou de alguma forma (novo número entrou)
                    if numeros_atuais != ultimo_historico_completo:
                        # O número novo é sempre o índice 0
                        novo_numero = numeros_atuais[0]
                        
                        timestamp = time.strftime('%H:%M:%S')
                        print(f"[{timestamp}] NOVO RESULTADO: {novo_numero}")
                        
                        with open("resultados_roleta.txt", "a") as f:
                            f.write(f"{novo_numero}\n")
                        
                        # Atualizamos o histórico completo para comparação na próxima volta
                        ultimo_historico_completo = numeros_atuais
                
                time.sleep(5)
                '''
                except Exception as inner_e:
                    print("Recuperando interface...")
                    try:
                        btn_stats.click()
                        time.sleep(1)
                        page.locator('button[data-tab-key="last500"]').click()
                    except: pass
                '''
        except Exception as e:
            print(f"\n[ERRO CRÍTICO]: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    executar_bot()