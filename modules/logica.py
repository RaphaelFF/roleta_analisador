import streamlit as st
import os
from .estrategias import JOGADAS
from .estilos import aplicar_cor_especial

def atualizar_numeros():
    """
    Lê o arquivo 'resultados.txt' e atualiza a lista de números sorteados na sessão.
    """
    try:
        with open('resultados.txt', 'r') as f:
            linhas = f.readlines()
            if linhas != st.session_state.ultimas_linhas_processadas:
                numeros = [int(linha.strip()) for linha in linhas if linha.strip().isdigit()]
                st.session_state.numeros_sorteados = numeros
                st.session_state.ultimas_linhas_processadas = linhas
    except FileNotFoundError:
        st.warning("Arquivo 'resultados.txt' não encontrado. Certifique-se de que o web scraper está rodando.")
        pass

@st.cache_data
def calcular_metricas(quantidade_sugerida, jogada_selecionada_key, sequencias_consecutivas, inverter_logica, inverter_logica_sequencia, numeros_sorteados):
    """
    Calcula e retorna o número de acertos e erros com base na jogada e quantidade de números selecionados.
    Usa cache para otimizar o desempenho.
    """
    acertos = 0
    erros = 0
    
    if numeros_sorteados:
        jogada_selecionada_obj = JOGADAS[jogada_selecionada_key]
        numeros_analise = numeros_sorteados[::-1][:quantidade_sugerida]
        
        for i, numero in enumerate(numeros_analise):
            indice_original = len(numeros_sorteados) - i - 1
            status = jogada_selecionada_obj.verificar(numero)
            
            cor_especial = aplicar_cor_especial(
                numero, status, jogada_selecionada_obj.verificar,
                numeros_sorteados, indice_original,
                sequencias_consecutivas,
                inverter_logica,
                inverter_logica_sequencia
            )
            
            if cor_especial:
                cor, _ = cor_especial
                if cor == 'blue':
                    acertos += 1
                elif cor == 'orange':
                    erros += 1

    return acertos, erros

def gerar_sinal():
    """
    Gera a mensagem de sinal de aposta quando um padrão é detectado.
    """
    if st.session_state.ativar_sinal and len(st.session_state.numeros_sorteados) >= 0:
        jogada_sinal_obj = JOGADAS[st.session_state.jogada_sinal]
        
        penultimo_numero = st.session_state.numeros_sorteados[-1]
        status_penultimo_numero = jogada_sinal_obj.verificar(penultimo_numero)

        sinal = aplicar_cor_especial(
            penultimo_numero, status_penultimo_numero, jogada_sinal_obj.verificar,
            st.session_state.numeros_sorteados, len(st.session_state.numeros_sorteados) - 0,
            st.session_state.sinal_sequencias_consecutivas,
            st.session_state.sinal_inverter_logica,
            st.session_state.sinal_inverter_logica_sequencia
        )

        if sinal and st.session_state.ultimo_sinal_numero != st.session_state.numeros_sorteados[-1]:
            st.session_state.ultimo_sinal_numero = st.session_state.numeros_sorteados[-1]
            cor_sinal, tipo_sinal = sinal
            st.session_state.current_signal_alert = f"""
            <div class="signal-card signal-card-{cor_sinal}">
                <h4>Sinal detectado: Após o número  {penultimo_numero}</h4>
                <span class="signal-number">Jogar no {st.session_state.jogada_sinal}</span><br>
            </div>
            """
        elif not sinal and st.session_state.ultimo_sinal_numero != st.session_state.numeros_sorteados[-1]:
            st.session_state.current_signal_alert = ""
    elif st.session_state.ativar_sinal:
         st.session_state.current_signal_alert = ""