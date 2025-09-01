from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import time

# --- Classe para esperar a mudança de texto ---
class text_has_changed:
    def __init__(self, locator, initial_text):
        self.locator = locator
        self.initial_text = initial_text

    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
            current_text = element.text
            return current_text != self.initial_text and current_text != ""
        except:
            return False

def salvar_numeros_em_arquivo(numeros):
    """Salva a lista de números em um arquivo de texto."""
    with open('resultados.txt', 'a') as f:
        # Junta a lista de números em uma única string separada por vírgulas
        f.write(f"{numeros}\n")

# Inicializa o driver do navegador
driver = webdriver.Chrome()
driver.get('https://app.stakehub.com.br/game/')

# Espera inicial para o contêiner do histórico estar visível
try:
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'grid.gap-1.h-full'))
    )
    print("Página e elementos principais carregados com sucesso.")
except Exception as e:
    print(f"Erro ao carregar a página principal: {e}")
    driver.quit()
    exit()

# Variável para armazenar a lista dos 10 últimos números
historico_recente = []

def get_historico_roleta():
    """Captura e retorna a lista completa de números do histórico da roleta."""
    try:
        historico_container = driver.find_element(By.CLASS_NAME, 'grid.gap-1.h-full')
        elementos_numeros = historico_container.find_elements(
            By.CSS_SELECTOR, 'div.flex.items-center.justify-center.font-bold'
        )
        numeros = [n.text for n in elementos_numeros if n.text.isdigit()]
        return numeros
    except Exception as e:
        print(f"Erro ao capturar o histórico: {e}")
        return []

# Loop principal para monitoramento
while True:
    historico_completo = get_historico_roleta()
    
    if historico_completo:
        initial_text = historico_completo[0]
        
        # Salva o histórico inicial no arquivo
        if historico_recente != historico_completo[:10]:
            historico_recente = historico_completo[:10]
            print("✅ HISTÓRICO INICIAL DETECTADO:")
            print(historico_recente)
            salvar_numeros_em_arquivo(historico_recente[0])

        print("\n🔁 Aguardando novo resultado...")
        
        try:
            first_number_element = WebDriverWait(driver, 60).until(
                text_has_changed((By.CSS_SELECTOR, 'div.flex.items-center.justify-center.font-bold'), initial_text)
            )
            
            # Se a espera for bem-sucedida, um novo número apareceu
            historico_completo = get_historico_roleta()
            
            historico_recente = historico_completo[:10]
            
            print("✅ NOVO NÚMERO DETECTADO:")
            print(historico_recente)
            salvar_numeros_em_arquivo(historico_recente[0])

        except Exception as e:
            print(f"Tempo de espera esgotado ou erro: {e}")
            pass