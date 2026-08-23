from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

LOG = []

def log(msg):
    print(msg)
    LOG.append(msg)

def rodar_diagnostico():
    driver = Driver(uc=True)
    problemas = []

    try:
        log(f"=== DIAGNÓSTICO GERAL - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ===\n")

        # --- PASSO 1: Acesso à página ---
        log("[1] Acesso à página")
        try:
            driver.get('https://mcgames.bet.br/games/playtech/roleta-brasileira')
            time.sleep(80)
            if 'roleta' in driver.title.lower() or 'mcgames' in driver.title.lower():
                log("    OK - Página carregou corretamente")
            else:
                log(f"    ALERTA - Título inesperado: '{driver.title}'")
        except Exception as e:
            log(f"    ERRO - Não foi possível acessar a página: {e}")
            problemas.append("Acesso à página")
            return problemas

        # --- PASSO 2: iframe#gameIframe ---
        log("\n[2] Iframe principal (iframe#gameIframe)")
        try:
            iframe_game = driver.find_element(By.ID, 'gameIframe')
            src = iframe_game.get_attribute('src') or ''
            log(f"    OK - Encontrado via ID. src começa com: '{src[:60]}...'")
            driver.switch_to.frame(iframe_game)
        except Exception as e:
            log(f"    ERRO - iframe#gameIframe não encontrado: {e}")
            log("    Buscando alternativas...")

            # Tenta por tag iframe com src contendo 'GameLauncher'
            try:
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                for i, f in enumerate(iframes):
                    src = f.get_attribute('src') or ''
                    if 'GameLauncher' in src or 'game' in src.lower():
                        log(f"    Alternativa encontrada - iframe[{i}] com src contendo 'GameLauncher'")
                        driver.switch_to.frame(f)
                        break
                else:
                    log("    NENHUM iframe de jogo encontrado")
                    problemas.append("Iframe principal")
                    return problemas
            except Exception as e2:
                log(f"    ERRO na busca alternativa: {e2}")
                problemas.append("Iframe principal")
                return problemas

        # --- PASSO 3: roulette-history_line ---
        log("\n[3] Elemento de histórico (roulette-history_line)")
        historico = None
        classe_encontrada = None

        # Tentativa 1: classe base exata
        try:
            historico = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'roulette-history_line'))
            )
            classe_encontrada = historico.get_attribute('class')
            log(f"    OK (tentativa 1) - classe base encontrada: '{classe_encontrada}'")
        except:
            log("    Tentativa 1 falhou (classe base)")

        # Tentativa 2: CSS parcial [class*='roulette-history_line']
        if not historico:
            try:
                historico = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='roulette-history_line']"))
                )
                classe_encontrada = historico.get_attribute('class')
                log(f"    OK (tentativa 2) - CSS parcial: '{classe_encontrada}'")
            except:
                log("    Tentativa 2 falhou (CSS parcial)")

        # Tentativa 3: classe com hash known
        if not historico:
            try:
                historico = driver.find_element(By.CSS_SELECTOR, "[class*='roulette-history']")
                classe_encontrada = historico.get_attribute('class')
                log(f"    OK (tentativa 3) - classe 'roulette-history': '{classe_encontrada}'")
            except:
                log("    Tentativa 3 falhou (classe roulette-history)")

        if not historico:
            log("    ERRO - Nenhum elemento de histórico encontrado")
            log("    Verificando se há iframes internos...")

            # Verifica se tem iframe dentro do gameIframe
            try:
                inner_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                log(f"    Iframes internos encontrados: {len(inner_iframes)}")
                for i, f in enumerate(inner_iframes):
                    src = f.get_attribute('src') or ''
                    log(f"      [{i}] src='{src[:80]}'")
            except:
                pass

            # Lista elementos do body para debug
            log("    Elementos no body:")
            try:
                body_els = driver.find_elements(By.XPATH, '/html/body/*')
                for el in body_els[:10]:
                    tag = el.tag_name
                    cls = el.get_attribute('class') or ''
                    log(f"      <{tag} class='{cls[:60]}'>")
            except:
                pass

            problemas.append("Elemento de histórico")
            return problemas

        # --- PASSO 4: Validação dos números ---
        log("\n[4] Validação dos números")
        try:
            texto = historico.text
            numeros = texto.split()
            log(f"    Texto bruto: '{texto[:60]}'")
            log(f"    Números extraídos: {numeros}")

            if not numeros:
                log("    ERRO - Lista de números vazia")
                problemas.append("Números vazios")
                return problemas

            validos = [n for n in numeros if n.isdigit() and 0 <= int(n) <= 36]
            invalidos = [n for n in numeros if not (n.isdigit() and 0 <= int(n) <= 36)]

            log(f"    Válidos (0-36): {validos}")
            if invalidos:
                log(f"    Inválidos: {invalidos}")
                problemas.append("Números inválidos")
            else:
                log(f"    OK - Todos os {len(validos)} números são válidos")

        except Exception as e:
            log(f"    ERRO ao processar números: {e}")
            problemas.append("Processamento de números")

        # --- RESULTADO ---
        log("\n" + "=" * 50)
        if not problemas:
            log("RESULTADO: SISTEMA OK - Todos os seletores funcionando")
            log(f"Últimos números capturados: {validos[:10]}")
        else:
            log(f"RESULTADO: SISTEMA COM PROBLEMAS")
            log(f"Problemas encontrados: {', '.join(problemas)}")
        log("=" * 50)

        return problemas

    except Exception as e:
        log(f"\nERRO GERAL INESPERADO: {e}")
        return ["Erro geral"]
    finally:
        # Salva relatório
        with open("diagnostico_geral.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(LOG))
        log(f"\nRelatório salvo em: diagnostico_geral.txt")
        driver.quit()


if __name__ == "__main__":
    rodar_diagnostico()
