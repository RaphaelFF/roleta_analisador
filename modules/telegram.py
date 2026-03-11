import time
import requests
import json
import os
from jogada import JOGADAS
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÕES GERAIS ---
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID') 
ARQUIVO_RESULTADOS = 'resultados_roleta.txt'
MAX_GALE = 3

# --- ESTRUTURA DE CORES ---
RESET_C, GREEN, RED, YELLOW, CYAN, BLUE, WHITE = "\033[0m", "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[94m", "\033[97m"

# --- CENTRAL DE ESTRATÉGIAS ---
CONFIG_ESTRATEGIAS = [
    {
        "id": "base_v34",
        "nome": "Vizinhos 34 (Base)",
        "tipo": "BASE",
        "jogada_a": "Vizinho 34",
        "tamanho_bloco": 3,
        "alvo_minimo": 2,
        "ativo": True
    },
    {
        "id": "alt_v",
        "nome": "Alternância (Inicia V)",
        "tipo": "ALTERNANCIA",
        "setup_grupo": "Pretos",
        "espera_grupo": "Vermelhos",
        "oposto_grupo": "Pretos",
        "tamanho_bloco": 4,
        "alvo_minimo": 2,
        "ativo": True
    },
    {
        "id": "alt_p",
        "nome": "Alternância (Inicia P)",
        "tipo": "ALTERNANCIA",
        "setup_grupo": "Vermelhos",
        "espera_grupo": "Pretos",
        "oposto_grupo": "Vermelhos",
        "tamanho_bloco": 4,
        "alvo_minimo": 2,
        "ativo": True
    }
]

# --- DICIONÁRIO DE RELATÓRIO DETALHADO ---
# Agora cada estratégia rastreia: Diretas, G1, G2, G3 e Reds
RELATORIO = {est['id']: {
    "nome": est['nome'],
    "direta": 0,
    "g1": 0,
    "g2": 0,
    "g3": 0,
    "reds": 0
} for est in CONFIG_ESTRATEGIAS}

# --- FUNÇÕES DE COMUNICAÇÃO ---

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"})
    except: pass

def msg_formatada(tipo, est_nome, gatilho=0, alvo=0, bloco=None, gale=0):
    if tipo == "ANALISE":
        msg = f"🔍 *ANÁLISE EM CURSO*\n\n📈 *Estratégia:* `{est_nome}`\n🚫 *Progresso:* `{gatilho}/{alvo}`\n🔢 *Últimos:* `{bloco}`"
    elif tipo == "ENTRADA":
        msg = f"⚠️ *ENTRADA CONFIRMADA*\n\n🎯 *Jogada:* `{est_nome}`\n💰 *Fazer:* Entrada Padrão"
    elif tipo == "GREEN":
        icon = "✅✅✅✅✅" if gale == 0 else "✅✅✅✅✅"
        msg = f"{icon} *GREEN NO ALVO!*\n\n📊 *Estratégia:* `{est_nome}`\n✨ *Resultado:* `{'DIRETO' if gale == 0 else f'GALE {gale}'}`"
    elif tipo == "RED":
        msg = f"❌❌❌❌❌ *RED FINAL*\n\n📉 *Estratégia:* `{est_nome}`\n⚠️ *Aviso:* Aguarde novo padrão."
    enviar_telegram(msg)

def gerar_relatorio_final():
    txt = "🏁 *RELATÓRIO DETALHADO DA SESSÃO*\n" + "─" * 20 + "\n"
    total_g = 0
    total_r = 0
    
    for id, d in RELATORIO.items():
        greens_est = d['direta'] + d['g1'] + d['g2'] + d['g3']
        total_g += greens_est
        total_r += d['reds']
        
        txt += f"🔹 *{d['nome']}*\n"
        txt += f"   🎯 Diretas: `{d['direta']}`\n"
        txt += f"   1️⃣ Gale 1: `{d['g1']}`\n"
        txt += f"   2️⃣ Gale 2: `{d['g2']}`\n"
        if MAX_GALE >= 3: txt += f"   3️⃣ Gale 3: `{d['g3']}`\n"
        txt += f"   ❌ Reds: `{d['reds']}`\n"
        txt += f"   📈 Winrate: `{((greens_est/(greens_est+d['reds']))*100 if (greens_est+d['reds']) > 0 else 0):.1f}%`\n\n"

    txt += "─" * 20 + f"\n🏆 *TOTAL GERAL:* `{total_g}G / {total_r}R`"
    enviar_telegram(txt)

def print_status_terminal(est_id):
    d = RELATORIO[est_id]
    total_g = d['direta'] + d['g1'] + d['g2'] + d['g3']
    print(f"{WHITE}[STATUS]{RESET_C} {d['nome']}: {GREEN}G:{total_g}{RESET_C} | {RED}R:{d['reds']}{RESET_C} (D:{d['direta']} G1:{d['g1']} G2:{d['g2']})")

# --- MOTORES DE LÓGICA (Mantidos) ---

def processar_base(bloco, jogada_nome):
    res = [JOGADAS[jogada_nome].verificar(n) for n in bloco]
    if res[-1] == 'errado' and all(x == 'certo' for x in res[:-1]): return "ERRO"
    if all(x == 'certo' for x in res): return "ACERTO"
    return "NADA"

def processar_alternancia(historico, setup_g, espera_g, oposto_g, tamanho):
    if len(historico) < (tamanho + 2): return "NADA", 0, None
    setup_nums = historico[-(tamanho+2) : -tamanho]
    if not all(JOGADAS[setup_g].verificar(n) == 'certo' for n in setup_nums): return "NADA", 1, None
    bloco = historico[-tamanho:]
    if 0 in bloco: return "NADA", 1, None
    for i, num in enumerate(bloco):
        alvo = espera_g if i % 2 == 0 else oposto_g
        if JOGADAS[alvo].verificar(num) != 'certo':
            if i == tamanho - 1: return "ERRO", tamanho + 2, setup_nums
            return "NADA", 1, None
    return "ACERTO", tamanho + 2, setup_nums

# --- LOOP PRINCIPAL ---

def monitorar():
    ponteiros = {est['id']: 0 for est in CONFIG_ESTRATEGIAS}
    gatilhos = {est['id']: 0 for est in CONFIG_ESTRATEGIAS}
    em_operacao = {est['id']: False for est in CONFIG_ESTRATEGIAS}
    gale_atual = {est['id']: 0 for est in CONFIG_ESTRATEGIAS}

    print(f"{BLUE}=== BOT MULTI-ESTRATÉGIA (RELATÓRIO PRO) ATIVO ==={RESET_C}")

    try:
        while True:
            if not os.path.exists(ARQUIVO_RESULTADOS): continue
            with open(ARQUIVO_RESULTADOS, 'r') as f:
                nums = [int(l.strip()) for l in f.readlines() if l.strip()]

            for est in CONFIG_ESTRATEGIAS:
                if not est['ativo']: continue
                pid = est['id']
                t = est['tamanho_bloco']
                req = t if est['tipo'] == "BASE" else t + 2

                while ponteiros[pid] <= len(nums) - req:
                    h_total = nums[:ponteiros[pid] + req]
                    bloco_focado = nums[ponteiros[pid] : ponteiros[pid] + t]
                    setup_info = None

                    if est['tipo'] == "BASE":
                        resultado = processar_base(bloco_focado, est['jogada_a'])
                        pulo = 1 if resultado == "NADA" else t
                    else:
                        resultado, pulo, setup_info = processar_alternancia(h_total, est['setup_grupo'], est['espera_grupo'], est['oposto_grupo'], t)

                    hora = time.strftime('%H:%M:%S')
                    
                    if resultado != "NADA":
                        if setup_info: print(f"{CYAN}[SETUP {est['nome']}]{RESET_C} {setup_info}")
                        
                        if not em_operacao[pid]:
                            if resultado == "ERRO":
                                gatilhos[pid] += 1
                                print(f"[{hora}] {YELLOW}{est['nome']}{RESET_C}: ERRO {gatilhos[pid]}/{est['alvo_minimo']}")
                                msg_formatada("ANALISE", est['nome'], gatilhos[pid], est['alvo_minimo'], h_total[-t:])
                                if gatilhos[pid] >= est['alvo_minimo']:
                                    em_operacao[pid], gale_atual[pid] = True, 0
                                    msg_formatada("ENTRADA", est['nome'])
                            elif resultado == "ACERTO": gatilhos[pid] = 0
                        else:
                            if resultado == "ACERTO":
                                # Registrar detalhadamente no relatório
                                if gale_atual[pid] == 0: RELATORIO[pid]['direta'] += 1
                                elif gale_atual[pid] == 1: RELATORIO[pid]['g1'] += 1
                                elif gale_atual[pid] == 2: RELATORIO[pid]['g2'] += 1
                                elif gale_atual[pid] == 3: RELATORIO[pid]['g3'] += 1

                                print(f"[{hora}] {GREEN}GREEN {est['nome']}!{RESET_C}")
                                print_status_terminal(pid)
                                msg_formatada("GREEN", est['nome'], gale=gale_atual[pid])
                                em_operacao[pid], gatilhos[pid] = False, 0
                            elif resultado == "ERRO":
                                if gale_atual[pid] < MAX_GALE:
                                    gale_atual[pid] += 1
                                    print(f"[{hora}] {BLUE}GALE {gale_atual[pid]} em {est['nome']}{RESET_C}")
                                    enviar_telegram(f"🔄 *GALE {gale_atual[pid]}* - {est['nome']}")
                                else:
                                    RELATORIO[pid]['reds'] += 1
                                    print(f"[{hora}] {RED}RED {est['nome']}!{RESET_C}")
                                    print_status_terminal(pid)
                                    msg_formatada("RED", est['nome'])
                                    em_operacao[pid], gatilhos[pid] = False, 0
                    
                    ponteiros[pid] += pulo
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Finalizando sistema... Gerando relatório PRO.{RESET_C}")
    finally:
        gerar_relatorio_final()
        print(f"{GREEN}Relatório detalhado enviado ao Telegram!{RESET_C}")

if __name__ == "__main__":
    monitorar()