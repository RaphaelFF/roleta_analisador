import streamlit as st
from streamlit_autorefresh import st_autorefresh
from modules.estrategias import JOGADAS
from modules.logica import atualizar_numeros, calcular_metricas, gerar_sinal
from modules.estilos import renderizar_numero
from modules.analise import analisar_regioes_quentes
import os

# --- 1. CONFIGURAÇÃO INICIAL DA PÁGINA ---
# Configura o layout da página para ocupar a largura total
st.set_page_config(layout="wide")

# Ativa a atualização automática do Streamlit a cada 5 segundos
st_autorefresh(interval=5000, key="auto_refresh")

# --- 2. INICIALIZAÇÃO DO ESTADO DE SESSÃO ---
DEFAULTS = {
    'numeros_sorteados': [],
    'ultimas_linhas_processadas': [],
    'acertos': 0,
    'erros': 0,
    'ultimo_sinal_numero': None,
    'current_signal_alert': "",
    'ativar_sinal': False,
    'jogada_selecionada': list(JOGADAS.keys())[0],
    'jogada_sinal': list(JOGADAS.keys())[0],
    'sequencias_consecutivas': 3,
    'sinal_sequencias_consecutivas': 3,
    'inverter_logica_sequencia': False,
    'inverter_logica': False,
    'sinal_inverter_logica_sequencia': False,
    'sinal_inverter_logica': False
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 3. CARREGAMENTO DO ESTILO CSS ---
with open(os.path.join("modules", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    st.title('Análise de Padrões na Roleta Europeia')
    
    # --- 4.1. BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.header("Configurações da Análise")
        st.selectbox('Selecione a Estratégia:', list(JOGADAS.keys()), key="jogada_selecionada")
        st.slider('Sequências consecutivas para análise', min_value=2, max_value=5, key="sequencias_consecutivas")
        st.checkbox('Analisar sequências de "erros"', help="Verifica sequências consecutivas de números que *não* fazem parte da estratégia escolhida.", key="inverter_logica_sequencia")
        st.checkbox('Analisar quebra de sequência', help="Ex: Se a estratégia for 3 acertos, a quebra acontece em 2 acertos + 1 erro.", key="inverter_logica")
        st.button('Limpar Números Sorteados', on_click=lambda: st.session_state.numeros_sorteados.clear())

        st.markdown("---")
        st.header("Avisador de Sinais")
        st.selectbox('Jogada do Sinal:', list(JOGADAS.keys()), key="jogada_sinal")
        st.slider('Sequências do Sinal', min_value=2, max_value=5, key="sinal_sequencias_consecutivas")
        st.checkbox('Ativar Avisador de Sinais', help="Ativa os alertas de aposta.", key="ativar_sinal")
        st.checkbox('Sinal: Sequência de "erros"', help="Alerta para sequências consecutivas de erros.", key="sinal_inverter_logica_sequencia")
        st.checkbox('Sinal: Quebra de sequência', help="Alerta para a quebra de uma sequência de acertos.", key="sinal_inverter_logica")
    
    # --- 4.2. CORPO PRINCIPAL DA INTERFACE ---
    st.header("Análise em Tempo Real")
    st.markdown("""
    **Legenda de Análise:**
    - 🟦 **Azul**: Padrão de Aposta Identificado
    - 🟧 **Laranja**: Quebra de Padrão Identificada
    - 🟩 **Verde**: Número que faz parte da estratégia escolhida.
    - 🟥 **Vermelho**: Número que *não* faz parte da estratégia escolhida.
    """, unsafe_allow_html=True) 

    gerar_sinal()
    
    # Slider para selecionar a quantidade de números a serem analisados
    if st.session_state.numeros_sorteados:
        quantidade_analise = st.slider(
            'Selecione a quantidade de números para a análise:',
            min_value=10,
            max_value=len(st.session_state.numeros_sorteados),
            value=min(30, len(st.session_state.numeros_sorteados)),
            key="quantidade_analise_slider"
        )
    else:
        quantidade_analise = 0

    # Atualiza as métricas de acertos e erros a partir do módulo 'logica'
    st.session_state.acertos, st.session_state.erros = calcular_metricas(
        quantidade_analise,
        st.session_state.jogada_selecionada,
        st.session_state.sequencias_consecutivas,
        st.session_state.inverter_logica,
        st.session_state.inverter_logica_sequencia,
        st.session_state.numeros_sorteados
    )
    
    # Exibe as métricas de desempenho em caixas
    st.subheader("Métricas de Desempenho")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-box metric-box-acerto"><h6>Acertos</h6><h3>{st.session_state.acertos}</h3></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box metric-box-erro"><h6>Erros</h6><h3>{st.session_state.erros}</h3></div>', unsafe_allow_html=True)
    
    st.markdown("---")

    # Exibe a análise de regiões quentes
    st.subheader("Análise de Regiões Quentes")
    if st.session_state.numeros_sorteados:
        contagens, regiao_quente = analisar_regioes_quentes(st.session_state.numeros_sorteados, quantidade_analise)

        cols = st.columns(len(contagens))
        for i, (nome, contagem) in enumerate(contagens.items()):
            with cols[i]:
                classe_cor = nome.replace(" ", "")
                st.markdown(f'<div class="hot-region-box hot-region-{classe_cor}"><h6>{nome}</h6><h3>{contagem}</h3></div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="hot-region-winner">
            <h4>A região mais quente é a dos **{regiao_quente}**</h4>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aguardando números para análise de regiões...")
    
    st.markdown("---")

    # Exibe a caixa de alerta de sinal se o padrão for detectado
    if st.session_state.current_signal_alert:
        st.markdown(st.session_state.current_signal_alert, unsafe_allow_html=True)

    # Contêiner para exibir a lista de números sorteados
    with st.container():
        if st.session_state.numeros_sorteados:
            num_colunas_exibicao = 8
            numeros_invertidos = st.session_state.numeros_sorteados[::-1]
            
            for i in range(0, len(numeros_invertidos), num_colunas_exibicao):
                row_numeros = numeros_invertidos[i:i + num_colunas_exibicao]
                cols = st.columns(len(row_numeros))
                for j, numero in enumerate(row_numeros):
                    renderizar_numero(cols[j], numero, i + j)
        else:
            st.info("Aguardando números sorteados...")
    
    atualizar_numeros()
    
if __name__ == "__main__":
    main()