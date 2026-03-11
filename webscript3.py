from seleniumbase import Driver
from selenium.webdriver.common.by import By
import time
import os

# Inicialização do Driver
driver = Driver(uc=True)

# URL da roleta Playtech
driver.get('https://mcgames.bet.br/games/playtech/roleta-brasileira')

janela = driver.window_handles[0]

# --- VARIÁVEIS DE CONTROLE ---
resultado = []
check_resultado = []
rodada = 0
ARQUIVO_RESULTADOS = "resultados_roleta.txt"

# --- CONFIGURAÇÃO DE REFRESH (25 MINUTOS) ---
TEMPO_REFRESH = 25 * 60  # 1500 segundos
ultima_atualizacao = time.time()

# Cores para o terminal
YELLOW = "\033[93m"
RESET_C = "\033[0m"

def api():
    global resultado
    try:
        driver.switch_to.window(janela)
        driver.switch_to.default_content()

        # Localização dos IFrames (Estrutura Playtech)
        iframe_1 = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[3]/div[1]/section/section[1]/div[2]/iframe')
        driver.switch_to.frame(iframe_1)

        shadow = driver.find_element(By.XPATH, '/html/body/game-container')
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow)

        iframe_2 = shadow_root.find_element(By.CSS_SELECTOR, 'iframe')
        driver.switch_to.frame(iframe_2)

        # Captura a linha de histórico
        resultado = driver.find_element(By.CLASS_NAME, 'roulette-history_line').text.split()
    except:
        # Se falhar aqui, provavelmente é porque a página deu refresh ou deslogou
        pass

# --- LOOP PRINCIPAL ---
print(f"{YELLOW}>>> CAPTURADOR INICIADO - MONITORANDO REFRESH A CADA 25MIN <<<{RESET_C}")

while True:
    try:
        # 1. VERIFICAÇÃO DE REFRESH PREVENTIVO
        agora = time.time()
        if agora - ultima_atualizacao > TEMPO_REFRESH:
            timestamp_refresh = time.strftime('%H:%M:%S')
            print(f"[{timestamp_refresh}] {YELLOW}EXECUTANDO REFRESH PREVENTIVO (ANTI-TIMEOUT)...{RESET_C}")
            
            driver.switch_to.default_content()
            driver.refresh() # Atualiza a página inteira
            
            ultima_atualizacao = agora
            time.sleep(10) # Aguarda 10 segundos para a página recarregar os IFrames
            continue # Volta para o topo do loop para tentar re-entrar nos IFrames

        # 2. CAPTURA DOS DADOS
        api()
        
        # Compara apenas os primeiros 10 números
        if resultado and resultado[0:10] != check_resultado:
            check_resultado = resultado[0:10]
            rodada += 1
            
            # Só grava e printa a partir da segunda mudança
            if rodada >= 2:
                novo_numero = resultado[0]
                timestamp = time.strftime('%H:%M:%S')
                
                # Salva no arquivo TXT
                with open(ARQUIVO_RESULTADOS, "a") as f:
                    f.write(f"{novo_numero}\n")
                
                print(f"[{timestamp}] NOVO RESULTADO: {novo_numero}")
                
        time.sleep(2)
        
    except Exception as e:
        time.sleep(2)
        pass