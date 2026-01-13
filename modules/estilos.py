import streamlit as st
from .estrategias import JOGADAS

def aplicar_cor_especial(numero, status, jogada_obj, numeros_sorteados, indice_atual, sequencias_consecutivas, inverter_logica, inverter_logica_sequencia):
    """
    Aplica cores especiais. Para 'vizinho 17 e 9', exige 2 números de intervalo sem gatilho.
    """
    
    # --- 1. REGRA: VIZINHO 17 E 9 COM INTERVALO DE DESCANSO ---
    if jogada_obj.nome == "vizinho 17 e 9":
        if indice_atual >= 1:
            # O número imediatamente anterior é o gatilho (17 ou 9)?
            if jogada_obj.eh_especial(numeros_sorteados[indice_atual - 1]):
                
                # Agora verificamos se houve um intervalo de 2 números sem gatilho antes dele
                intervalo_limpo = True
                
                # Checa o 2º número atrás (se existir)
                if indice_atual >= 2:
                    if jogada_obj.eh_especial(numeros_sorteados[indice_atual - 2]):
                        intervalo_limpo = False
                
                # Checa o 3º número atrás (se existir)
                if indice_atual >= 3:
                    if jogada_obj.eh_especial(numeros_sorteados[indice_atual - 3]):
                        intervalo_limpo = False
                
                # Só marca se o anterior for gatilho E os dois antes dele NÃO forem
                if intervalo_limpo:
                    return ('blue', numero) if status == 'certo' else ('orange', numero)
                    
        return None # Se não passar no critério, não pinta nada

    # --- 2. REGRA PARA AS OUTRAS JOGADAS (Mantém o padrão original) ---
    status_alvo = 'errado' if inverter_logica_sequencia else 'certo'
    if indice_atual >= sequencias_consecutivas - 1:
        # ... (restante do código original que você já tem para sequências)
        consecutivos = all(
            jogada_obj.verificar(numeros_sorteados[indice_atual - k]) == status_alvo
            for k in range(1, sequencias_consecutivas)
        )
        
        proximo_nao_alvo = (
            indice_atual - sequencias_consecutivas < 0 or
            jogada_obj.verificar(numeros_sorteados[indice_atual - sequencias_consecutivas]) != status_alvo
        )
        
        if consecutivos and proximo_nao_alvo:
            if inverter_logica:
                if status == 'errado': return 'blue', numero
                elif status == 'certo': return 'orange', numero
            else:
                if status == 'certo': return 'blue', numero
                elif status == 'errado': return 'orange', numero
                
    return None

def formatar_numero(numero, cor):
    """
    Retorna o HTML para formatar o número com a cor e o estilo corretos.
    """
    classe_cor = "numero-zero" if numero == 0 else f"numero-{cor}"
    return f"""
    <div class="numero-container">
        <span class="{classe_cor}">{numero}</span>
    </div>
    """

def renderizar_numero(col, numero, indice_exibicao):
    indice_original = len(st.session_state.numeros_sorteados) - indice_exibicao - 1
    
    if st.session_state.jogada_selecionada in JOGADAS and indice_original >= 0:
        jogada_selecionada_obj = JOGADAS[st.session_state.jogada_selecionada]
        status = jogada_selecionada_obj.verificar(numero)
        
        # PASSANDO O OBJETO COMPLETO (jogada_selecionada_obj)
        cor_especial = aplicar_cor_especial(
            numero, status, jogada_selecionada_obj, 
            st.session_state.numeros_sorteados, indice_original,
            st.session_state.sequencias_consecutivas,
            st.session_state.inverter_logica,
            st.session_state.inverter_logica_sequencia
        )
        
        if cor_especial:
            cor, _ = cor_especial
        else:
            cor = 'green' if status == 'certo' else 'red'
        
        col.markdown(formatar_numero(numero, cor), unsafe_allow_html=True)