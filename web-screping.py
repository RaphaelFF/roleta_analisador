from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

load_dotenv()

# --- Credenciais de login ---
USUARIO = os.getenv('USUARIO')
SENHA = os.getenv('SENHA')
URL_INICIAL = os.getenv('URL_INICIAL')
URL_JOGO = os.getenv('URL_JOGO')


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

def salvar_numero_em_arquivo(numero):
    """Salva um único número no arquivo, em modo de adição."""
    with open('resultados.txt', 'a') as f:
        f.write(f"{numero}\n")

def fazer_login_e_acessar_jogo(driver, url_inicial, url_jogo):
    """Navega até a página de login, realiza o login e acessa a roleta."""
    driver.get(url_inicial)

    try:
        # 1. Clicar no botão "Avançar" para fechar o pop-up, se existir
        try:
            botao_avancar = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Avançar')]"))
            )
            botao_avancar.click()
            print("Pop-up 'Avançar' fechado com sucesso.")
        except:
            print("Pop-up 'Avançar' não encontrado ou já fechado.")
        
        # 2. Preencher e-mail e senha
        campo_email = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'email'))
        )
        campo_email.send_keys(USUARIO)
        
        campo_senha = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'password'))
        )
        campo_senha.send_keys(SENHA)

        # 3. Clicar no botão "Entrar"
        botao_entrar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        botao_entrar.click()
        print("Login realizado com sucesso.")

        # --- CORREÇÃO APLICADA AQUI: By.CLASS_NAME foi trocado por By.CSS_SELECTOR ---
        # 4. Esperar que a div de container de jogos carregue
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.grid.grid-cols-1.sm\\:grid-cols-2.lg\\:grid-cols-3.xl\\:grid-cols-4.gap-3.sm\\:gap-4'))
        )
        print("Container de jogos carregado. Procurando o link da Roleta Brasileira...")
        
        # 5. Encontrar e clicar no link da roleta usando o atributo href
        link_roleta = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@href='{url_jogo}']"))
        )
        link_roleta.click()
        print("Navegação para a Roleta Brasileira realizada com sucesso.")
        
        return True
    
    except Exception as e:
        print(f"Erro durante o login ou navegação: {e}")
        return False

def get_historico_roleta(driver):
    """Captura e retorna a lista completa de números do histórico da roleta."""
    try:
        historico_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'grid.gap-1.h-full'))
        )
        elementos_numeros = historico_container.find_elements(
            By.CSS_SELECTOR, 'div.flex.items-center.justify-center.font-bold'
        )
        numeros = [n.text for n in elementos_numeros if n.text.isdigit()]
        return numeros
    except Exception as e:
        print(f"Erro ao capturar o histórico: {e}")
        return []

# --- Lógica Principal ---
driver = webdriver.Chrome()

if not fazer_login_e_acessar_jogo(driver, URL_INICIAL, URL_JOGO):
    driver.quit()
    exit()

# Aguarda a página do jogo carregar completamente
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'grid.gap-1.h-full'))
)
print("Página do jogo carregada com sucesso. Iniciando monitoramento.")

historico_recente = []

while True:
    historico_completo = get_historico_roleta(driver)
    
    if historico_completo:
        initial_text = historico_completo[0]
        
        # Salva o número mais recente do histórico
        if historico_recente != historico_completo[:10]:
            historico_recente = historico_completo[:10]
            print("✅ HISTÓRICO ATUALIZADO:")
            print(historico_recente)
            salvar_numero_em_arquivo(historico_recente[0])

        print("\n🔁 Aguardando novo resultado...")
        
        try:
            WebDriverWait(driver, 60).until(
                text_has_changed((By.CSS_SELECTOR, 'div.flex.items-center.justify-center.font-bold'), initial_text)
            )
            
            historico_completo = get_historico_roleta(driver)
            
            historico_recente = historico_completo[:10]
            
            print("✅ NOVO NÚMERO DETECTADO:")
            print(historico_recente)
            salvar_numero_em_arquivo(historico_recente[0])

        except Exception as e:
            print(f"Tempo de espera esgotado ou erro: {e}")
            pass