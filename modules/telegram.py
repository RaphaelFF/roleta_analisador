import time
from jogada import JOGADAS
from cores import aplicar_cor_especial

# Configurações
ALVO_MINIMO = 3
ARQUIVO_RESULTADOS = 'resultados_roleta.txt'
ARQUIVO_ALERTAS = 'alertas_telegram_simulacao.txt'

def monitorar_estrategia():
    print("Iniciando monitoramento (Incremento e Quebra)...")
    
    linhas_processadas = 0
    tamanho_lista_especial_anterior = 0
    cor_da_ultima_sequencia = None 

    # Configurações da estratégia (Baseadas no seu sistema)
    jogada_nome = "Vizinho 34"
    seq_cons_interface = 3
    inv_log = False
    inv_log_seq = False

    while True:
        try:
            with open(ARQUIVO_RESULTADOS, 'r') as f:
                linhas = f.readlines()
            
            if len(linhas) > linhas_processadas:
                numeros_sorteados = [int(l.strip()) for l in list(linhas) if l.strip()]
                
                if numeros_sorteados:
                    cores_especiais = obter_lista_cores_especiais(
                        numeros_sorteados, jogada_nome, seq_cons_interface, inv_log, inv_log_seq
                    )
                    
                    # Verifica se uma nova cor especial (azul ou laranja) foi detectada
                    if len(cores_especiais) > tamanho_lista_especial_anterior:
                        nova_cor = cores_especiais[-1]
                        
                        # 1. LÓGICA DE QUEBRA
                        if cor_da_ultima_sequencia and nova_cor != cor_da_ultima_sequencia:
                            nome_cor_quebrada = "AZUL" if cor_da_ultima_sequencia == 'blue' else "LARANJA"
                            disparar_alerta(f"STATUS: Sequência {nome_cor_quebrada} quebrada. Analisando...")
                        
                        # 2. LÓGICA DE INCREMENTO
                        # Conta quantos elementos iguais existem no final da lista
                        contador_atual = 0
                        for c in reversed(cores_especiais):
                            if c == nova_cor:
                                contador_atual += 1
                            else:
                                break
                        
                        # Só dispara se atingir o alvo mínimo ou for um incremento superior a ele
                        if contador_atual >= ALVO_MINIMO:
                            nome_cor_atual = "AZUIS" if nova_cor == 'blue' else "LARANJAS"
                            disparar_alerta(f"ALERTA: Identificado {contador_atual} {nome_cor_atual} seguidos!")
                        
                        # Atualiza estados para o próximo loop
                        cor_da_ultima_sequencia = nova_cor
                        tamanho_lista_especial_anterior = len(cores_especiais)
                
                linhas_processadas = len(linhas)
        
        except FileNotFoundError:
            pass
        
        time.sleep(2)

def obter_lista_cores_especiais(numeros, jogada_nome, seq_cons, inv_log, inv_log_seq):
    """Filtra o histórico para retornar apenas as cores blue/orange conforme cores.py"""
    jogada_obj = JOGADAS[jogada_nome]
    lista_especial = []
    for i, num in enumerate(numeros):
        status = jogada_obj.verificar(num)
        cor_info = aplicar_cor_especial(num, status, jogada_obj.verificar, numeros, i, seq_cons, inv_log, inv_log_seq)
        if cor_info:
            lista_especial.append(cor_info[0])
    return lista_especial

def disparar_alerta(mensagem):
    timestamp = time.strftime('%H:%M:%S')
    msg_formatada = f"[{timestamp}] {mensagem}"
    print(msg_formatada)
    with open(ARQUIVO_ALERTAS, 'a') as f:
        f.write(msg_formatada + "\n")

if __name__ == "__main__":
    monitorar_estrategia()