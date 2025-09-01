def aplicar_cor_especial(numero, status, jogada_selecionada, numeros_sorteados, indice_atual, sequencias_consecutivas, inverter_logica, inverter_logica_sequencia):
    status_alvo = 'errado' if inverter_logica_sequencia else 'certo'
    
    if indice_atual >= sequencias_consecutivas - 1:
        consecutivos = all(
            jogada_selecionada(numeros_sorteados[indice_atual - k]) == status_alvo
            for k in range(1, sequencias_consecutivas)
        )
        
        proximo_nao_alvo = (
            indice_atual - sequencias_consecutivas < 0 or
            jogada_selecionada(numeros_sorteados[indice_atual - sequencias_consecutivas]) != status_alvo
        )
        
        if consecutivos and proximo_nao_alvo:
            if inverter_logica:
                if status == 'errado':
                    return 'blue', numero
                elif status == 'certo':
                    return 'orange', numero
            else:
                if status == 'certo':
                    return 'blue', numero
                elif status == 'errado':
                    return 'orange', numero
    return None

def formatar_numero(numero, cor):
    cores = {
        'blue': 'blue',
        'orange': 'orange',
        'certo': 'green',
        'errado': 'red'
    }
    return f'<div style="background-color: {cores[cor]}; color: white; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin: 5px;">{numero}</div>'