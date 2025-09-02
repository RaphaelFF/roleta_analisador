import streamlit as st
from .estrategias import JOGADAS

def aplicar_cor_especial(numero, status, jogada_selecionada, numeros_sorteados, indice_atual, sequencias_consecutivas, inverter_logica, inverter_logica_sequencia):
    """
    Aplica cores especiais (azul/laranja) a números que correspondem a um padrão de aposta.
    """
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
    """
    Renderiza um número na tela com a cor de análise correta.
    """
    indice_original = len(st.session_state.numeros_sorteados) - indice_exibicao - 1
    
    if st.session_state.jogada_selecionada in JOGADAS and indice_original >= 0:
        jogada_selecionada_obj = JOGADAS[st.session_state.jogada_selecionada]
        status = jogada_selecionada_obj.verificar(numero)
        
        cor = None
        
        cor_especial = aplicar_cor_especial(
            numero, status, jogada_selecionada_obj.verificar,
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