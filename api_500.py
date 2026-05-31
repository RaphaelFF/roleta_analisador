from seleniumbase import Driver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
ARQUIVO_BASELINE = "ultimos_500.txt"
YELLOW, GREEN, RED, RESET_C = "\033[93m", "\033[92m", "\033[91m", "\033[0m"
driver = Driver(uc=True)

driver.get('https://mcgames.bet.br/games/playtech/roleta-brasileira')

janela = driver.window_handles[0]

while len(driver.find_elements(By.XPATH, '/html/body/div[1]/div[1]/div[3]/div[1]/section/section[1]/div[2]/iframe')) == 0:
    time.sleep(1)

iframe_1 = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[3]/div[1]/section/section[1]/div[2]/iframe')
driver.switch_to_frame(iframe_1)

while len(driver.find_elements(By.XPATH, '/html/body/game-container')) == 0:
    time.sleep(1)

shadow = driver.find_element(By.XPATH, '/html/body/game-container')

shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow)

while len(shadow_root.find_elements(By.CSS_SELECTOR, 'iframe')) == 0:
    time.sleep(1)

iframe_2 = shadow_root.find_element(By.CSS_SELECTOR, 'iframe')

driver.switch_to_frame(iframe_2)
# 1) clicar no botão “últimos 500 números”
botao_500 = WebDriverWait(driver, 60).until(
    EC.element_to_be_clickable(
        (By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[1]/div[1]/ul/li[5]')
    )
)
botao_500.click()

# 2) aguardar os resultados aparecerem

WebDriverWait(driver, 60).until(
    EC.presence_of_element_located(
        (By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[2]/div[3]/div/div[2]/div/div/div/div/div/div/div/div/div')
    )
)

result = []

try:
    result = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[2]/div[3]/div/div[2]/div/div/div/div/div/div/div/div/div').text.split()
    #print(f'result 1 {result}')
except:
    pass
print(f"resultado dos ultimos: {result}")

if result:
        re = result[0:500]
        result_cronologico = re[::-1]
        
        with open(ARQUIVO_BASELINE, "w") as f:
            for num in result_cronologico:
                f.write(f"{num}\n")
        
        print(f"{GREEN}>>> SUCESSO: {len(result_cronologico)} números salvos.{RESET_C}")
else:
        print(f"{RED}>>> ERRO: Lista de números vazia.{RESET_C}")