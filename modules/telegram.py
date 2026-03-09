import time
import requests
import json
import os
import sys
import signal
from jogada import JOGADAS
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID') 
ALVO_MINIMO = 3 
MAX_GALE = 2 
ARQUIVO_RESULTADOS = 'resultados_roleta.txt'
ARQUIVO_PLACAR = 'placar_detalhado.json'
ESTRATEGIA_NOME = "Vizinho 34"

# --- CORES PARA TERMINAL ---
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"

# --- GESTÃO DE DADOS ---
def resetar_placar():
    dados_vazios = {"greens": 0, "reds": 0, "gale0": 0, "gale1": 0, "gale2": 0}
    with open(ARQUIVO_PLACAR, 'w') as f:
        json.dump(dados_vazios, f)
    return dados_vazios

def carregar_placar():
    if not os.path.exists(ARQUIVO_PLACAR):
        return resetar_placar()
    try:
        with open(ARQUIVO_PLACAR, 'r') as f:
            return json.load(f)
    except:
        return resetar_placar()

def salvar_placar(placar):
    with open(ARQUIVO_PLACAR, 'w') as f:
        json.dump(placar, f)

def enviar_telegram(mensagem):
    hora_atual = time.strftime('%H:%M:%S')
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": f"🕒 `[{hora_atual}]` \n{mensagem}", "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except: pass

# --- RELATÓRIO ---
def gerar_relatorio_final():
    placar = carregar_placar()
    total = placar['greens'] + placar['reds']
    win_rate = (placar['greens'] / total * 100) if total > 0 else 0
    return (
        "📊 *RELATÓRIO FINAL DA SESSÃO*\n\n"
        f"✅ *Total de Greens:* {placar['greens']}\n"
        f"❌ *Total de Reds:* {placar['reds']}\n"
        f"📈 *Assertividade:* {win_rate:.2f}%\n\n"
        "--- *DETALHAMENTO* ---\n"
        f"🟢 Direto: {placar['gale0']}\n"
        f"🟡 Gale 1: {placar['gale1']}\n"
        f"🟠 Gale 2: {placar['gale2']}\n"
        "\n♻️ _Sessão encerrada e placar zerado._"
    )

def fechar_sistema(signum, frame):
    print(f"\n{YELLOW}{BOLD}Gerando relatório e limpando dados...{RESET}")
    enviar_telegram(gerar_relatorio_final())
    resetar_placar()
    sys.exit(0)

signal.signal(signal.SIGINT, fechar_sistema)

def get_status(n):
    return JOGADAS[ESTRATEGIA_NOME].verificar(n)

def log_terminal(trio, tipo, contagem=None, em_operacao=False, resultado=None, gale=0):
    hora = time.strftime('%H:%M:%S')
    trio_str = f"[{', '.join(map(str, trio))}]"
    if not em_operacao:
        if tipo == 'ERRO':
            print(f"{YELLOW}[{hora}] SCANNER:{RESET} {trio_str} -> {RED}ERRO {contagem}/{ALVO_MINIMO}{RESET}")
        else:
            print(f"{CYAN}[{hora}] Monitorando fluxo...{RESET}", end="\r")
    else:
        label = f"GALE {gale}" if gale > 0 else "ENTRADA"
        if resultado == 'GREEN':
            print(f"\n{GREEN}{BOLD}[{hora}] ✅ GREEN NO {label}! {RESET} Bloco: {trio_str}")
        elif resultado == 'RED':
            print(f"\n{RED}{BOLD}[{hora}] ❌ RED FINAL! {RESET} Bloco: {trio_str}")
        else:
            print(f"{MAGENTA}[{hora}] 🎲 {label} ATIVA: {RESET} Analisando {trio_str}...")

def monitorar_estrategia():
    placar = resetar_placar() 
    print(f"\n{BOLD}{BLUE}=========================================={RESET}")
    print(f"{BOLD}{BLUE}      BOT INICIADO - PLACAR ZERADO        {RESET}")
    print(f"{BOLD}{BLUE}=========================================={RESET}\n")
    enviar_telegram(f"🚀 *SESSÃO INICIADA*\nEstratégia: `{ESTRATEGIA_NOME}`")

    ponteiro = 0
    if os.path.exists(ARQUIVO_RESULTADOS):
        with open(ARQUIVO_RESULTADOS, 'r') as f:
            ponteiro = len([l for l in f.readlines() if l.strip()])

    contador_gatilho = 0
    em_operacao = False
    gale_atual = 0

    while True:
        try:
            with open(ARQUIVO_RESULTADOS, 'r') as f:
                nums = [int(l.strip()) for l in f.readlines() if l.strip()]
            
            while ponteiro <= len(nums) - 3:
                trio = nums[ponteiro : ponteiro + 3]
                res = [get_status(n) for n in trio]
                
                if not em_operacao:
                    if res == ['certo', 'certo', 'errado']:
                        pre_valido = True
                        if ponteiro > 0 and get_status(nums[ponteiro - 1]) == 'certo':
                            pre_valido = False
                        
                        if pre_valido:
                            contador_gatilho += 1
                            log_terminal(trio, 'ERRO', contagem=contador_gatilho)
                            ponteiro += 3
                            if contador_gatilho >= ALVO_MINIMO:
                                em_operacao = True
                                gale_atual = 0
                                enviar_telegram(f"⚠️ *SINAL CONFIRMADO* ({ALVO_MINIMO} Erros)\n*FAÇA A ENTRADA AGORA!*")
                        else:
                            ponteiro += 1
                    else:
                        ponteiro += 1
                        log_terminal(trio, 'BUSCA')
                
                else:
                    deu_green = (res == ['certo', 'certo', 'certo'])
                    deu_red = (res == ['certo', 'certo', 'errado'])

                    if deu_green:
                        placar['greens'] += 1
                        placar[f"gale{gale_atual}"] += 1
                        salvar_placar(placar)
                        log_terminal(trio, 'ACERTO', em_operacao=True, resultado='GREEN', gale=gale_atual)
                        info_gale = f"Gale {gale_atual}" if gale_atual > 0 else "Direto"
                        enviar_telegram(f"✅ *GREEN {info_gale.upper()}!*\nBloco: `{trio}`\n📊 Placar: {placar['greens']}G | {placar['reds']}R")
                        em_operacao = False
                        contador_gatilho = 0
                        ponteiro += 3
                    elif deu_red:
                        if gale_atual < MAX_GALE:
                            gale_atual += 1
                            # --- AVISO DE GALE NO TELEGRAM ---
                            enviar_telegram(f"🔄 *BLOCO DE ERRO:* `{trio}`\n*INDICAÇÃO:* Partindo para o **GALE {gale_atual}**!")
                            
                            log_terminal(trio, 'ERRO', em_operacao=True, gale=gale_atual)
                            ponteiro += 3
                        else:
                            placar['reds'] += 1
                            salvar_placar(placar)
                            log_terminal(trio, 'ERRO', em_operacao=True, resultado='RED', gale=gale_atual)
                            enviar_telegram(f"❌ *RED FINAL*\nBloco: `{trio}`\n📊 Placar: {placar['greens']}G | {placar['reds']}R")
                            em_operacao = False
                            contador_gatilho = 0
                            ponteiro += 3
                    else:
                        ponteiro += 1
            time.sleep(1)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    monitorar_estrategia()