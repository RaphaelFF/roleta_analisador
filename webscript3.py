from seleniumbase import Driver
from selenium.webdriver.common.by import By
import time

# Inicialização do Driver
driver = Driver(uc=True)

# URL da roleta Playtech
driver.get('https://mcgames.bet.br/games/playtech/roleta-brasileira')

janela = driver.window_handles[0]

# --- VARIÁVEIS DE CONTROLE ORIGINAIS (MANTIDAS) ---
resultado = []
check_resultado = []
rodada = 0
ARQUIVO_RESULTADOS = "resultados_roleta.txt"

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
        pass

# --- LOOP COM A SUA LÓGICA E VISUAL PADRONIZADO ---
while True:
    try:
        api()
        
        # Compara apenas os primeiros 10 números (sua lógica original)
        if resultado[0:10] != check_resultado:
            check_resultado = resultado[0:10]
            
            rodada += 1
            
            # Só grava e printa a partir da segunda mudança (sua lógica original)
            if rodada >= 2:
                novo_numero = resultado[0]
                timestamp = time.strftime('%H:%M:%S')
                
                # Salva no arquivo TXT
                with open(ARQUIVO_RESULTADOS, "a") as f:
                    f.write(f"{novo_numero}\n")
                
                # --- SAÍDA PADRONIZADA IGUAL AO WEBSCRIPT.PY ---
                print(f"[{timestamp}] NOVO RESULTADO: {novo_numero}")
                
        time.sleep(2)
    except Exception as e:
        time.sleep(1)
        pass