from seleniumbase import Driver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
botao_500 = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable(
        (By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[1]/div[1]/ul/li[5]')
    )
)
botao_500.click()

# 2) aguardar os resultados aparecerem
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located(
        (By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[2]/div[4]/div/div[2]/div/div/div/div/div/div')
    )
)

result = []

try:
    result = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[2]/div[4]/div/div[2]/div/div/div/div/div/div').text.split()
    #print(f'result 1 {result}')
except:
    pass

try:
    result = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[1]/div/div/div[2]/div[4]/div/div[2]/div/div/div/div/div/div/div/div/div').text.split()
    #print(f'result 2 {result}/n')
except:
    pass

resultado = []
check_resultado = []
rodada = 0

def api():

    global resultado

    driver.switch_to.window(janela)

    iframe_1 = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[3]/div[1]/section/section[1]/div[2]/iframe')

    driver.switch_to.frame(iframe_1)

    shadow = driver.find_element(By.XPATH, '/html/body/game-container')

    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow)

    iframe_2 = shadow_root.find_element(By.CSS_SELECTOR, 'iframe')

    driver.switch_to.frame(iframe_2)

    try:
        resultado = driver.find_element(By.CLASS_NAME, 'roulette-history_line').text.split()
    except:
        pass

    try:
        resultado = driver.find_element(By.CLASS_NAME, 'roulette-history_line--MmqqV').text.split()
    except:
        pass

    return resultado

while True:
    
    try:
        api()
        
        if resultado[0:10] != check_resultado:
            check_resultado = resultado[0:10]
            
            #print(rodada)
            rodada += 1
            
            if rodada >= 2:
                
                result.insert(0, resultado[0])
                #salvar result.insert(0, resultado[0]) no txt
                print(resultado)
    except:
        pass
    
    