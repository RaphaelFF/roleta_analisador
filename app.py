import streamlit as st
from streamlit_autorefresh import st_autorefresh
from modules.jogada import JOGADAS
from modules.cores import aplicar_cor_especial, formatar_numero
from modules.analises import analisar_regioes_quentes
import os

st.set_page_config(layout="wide")

if 'numeros_sorteados' not in st.session_state:
    st.session_state.numeros_sorteados = []
if 'ultimas_linhas_processadas' not in st.session_state:
    st.session_state.ultimas_linhas_processadas = []
if 'acertos' not in st.session_state:
    st.session_state.acertos = 0
if 'erros' not in st.session_state:
    st.session_state.erros = 0

# A cada 5 segundos, a função atualizar_numeros será executada
st_autorefresh(interval=5000, key="auto_refresh")

def atualizar_numeros():
    """Lê o arquivo de resultados e atualiza a lista de números no estado da sessão."""
    try:
        with open('resultados.txt', 'r') as f:
            linhas = f.readlines()
            
            if linhas != st.session_state.ultimas_linhas_processadas:
                numeros = [int(linha.strip()) for linha in linhas if linha.strip().isdigit()]
                st.session_state.numeros_sorteados = numeros
                st.session_state.ultimas_linhas_processadas = linhas
                st.rerun()
                
    except FileNotFoundError:
        st.warning("Arquivo 'resultados.txt' não encontrado. Certifique-se de que o web scraper está rodando.")
        pass

def calcular_metricas():
    """Calcula e atualiza as métricas de acertos e erros com base na lógica de filtragem atual."""
    acertos = 0
    erros = 0
    
    if st.session_state.numeros_sorteados:
        jogada_selecionada_obj = JOGADAS[st.session_state.jogada_selecionada]
        
        numeros_analise = st.session_state.numeros_sorteados[::-1]
        
        for i, numero in enumerate(numeros_analise):
            indice_original = len(st.session_state.numeros_sorteados) - i - 1
            status = jogada_selecionada_obj.verificar(numero)
            
            cor_especial = aplicar_cor_especial(
                numero, status, jogada_selecionada_obj.verificar,
                st.session_state.numeros_sorteados, indice_original,
                st.session_state.sequencias_consecutivas,
                st.session_state.inverter_logica,
                st.session_state.inverter_logica_sequencia
            )
            
            if cor_especial:
                cor, _ = cor_especial
                if cor == 'blue':
                    acertos += 1
                elif cor == 'orange':
                    erros += 1

    st.session_state.acertos = acertos
    st.session_state.erros = erros

# CSS para controlar a responsividade
_RESPONSIVE_CSS = """
<style>
/* Remove o empilhamento em telas pequenas */
@media (max-width: 640px) {
    .st-emotion-cache-1yiv2bg {
        min-width: 0;
    }
}

/* Define uma largura máxima para o contêiner de números para torná-lo compacto */
.st-emotion-cache-ocqkz7 {
    max-width: 700px;
}
</style>
"""

def render_numero(col, numero, indice_exibicao):
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


def main():
    st.title('Análise de Padrões na Roleta Europeia')
    
    with st.sidebar:
        st.header("Configurações da Análise")
        if 'jogada_selecionada' not in st.session_state or st.session_state.jogada_selecionada not in JOGADAS:
            st.session_state.jogada_selecionada = list(JOGADAS.keys())[0]
        st.session_state.jogada_selecionada = st.selectbox('Selecione a Estratégia:', list(JOGADAS.keys()), index=list(JOGADAS.keys()).index(st.session_state.jogada_selecionada))
        
        st.session_state.sequencias_consecutivas = st.slider('Sequências consecutivas para análise', min_value=2, max_value=5, value=st.session_state.get('sequencias_consecutivas', 3))
        st.session_state.inverter_logica_sequencia = st.checkbox('Analisar sequências de "erros"', help="Verifica sequências consecutivas de números que *não* fazem parte da estratégia escolhida.", value=st.session_state.get('inverter_logica_sequencia', False))
        st.session_state.inverter_logica = st.checkbox('Analisar quebra de sequência', help="Ex: Se a estratégia for 3 acertos, a quebra acontece em 2 acertos + 1 erro.", value=st.session_state.get('inverter_logica', False))
        
        st.button('Limpar Números Sorteados', on_click=lambda: st.session_state.numeros_sorteados.clear())

    st.header("Análise em Tempo Real")
    st.markdown("""
    **Legenda de Análise:**
    - 🟦 **Azul**: Aposta Certa (padrão identificado)
    - 🟧 **Laranja**: Aposta Errada (padrão identificado)
    - 🟩 **Verde**: Número que faz parte da estratégia escolhida.
    - 🟥 **Vermelho**: Número que *não* faz parte da estratégia escolhida.
    """)

    st.markdown(_RESPONSIVE_CSS, unsafe_allow_html=True)
    
    calcular_metricas()
    
    st.subheader("Métricas de Desempenho")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Acertos (Azul)", value=st.session_state.acertos)
    with col2:
        st.metric(label="Total de Erros (Laranja)", value=st.session_state.erros)
    
    st.markdown("---")

    st.subheader("Análise de Regiões Quentes")
    if st.session_state.numeros_sorteados:
        
        # Adicione o controle deslizante para selecionar a quantidade de números
        quantidade_analise = st.slider(
            'Selecione a quantidade de números para a análise:',
            min_value=10,
            max_value=len(st.session_state.numeros_sorteados),
            value=min(30, len(st.session_state.numeros_sorteados))
        )

        contagens, regiao_quente = analisar_regioes_quentes(st.session_state.numeros_sorteados, quantidade_analise)
        
        cols = st.columns(len(contagens))
        for i, (nome, contagem) in enumerate(contagens.items()):
            cols[i].metric(label=f"{nome}", value=f"{contagem}")
        
        st.markdown(f"#### A região mais quente é a dos **{regiao_quente}**")
    else:
        st.info("Aguardando números para análise de regiões...")
    
    st.markdown("---")
    
    with st.container():
        if st.session_state.numeros_sorteados:
            num_colunas_exibicao = 8
            numeros_invertidos = st.session_state.numeros_sorteados[::-1]
            
            for i in range(0, len(numeros_invertidos), num_colunas_exibicao):
                row_numeros = numeros_invertidos[i:i + num_colunas_exibicao]
                cols = st.columns(len(row_numeros))
                for j, numero in enumerate(row_numeros):
                    render_numero(cols[j], numero, i + j)
        else:
            st.info("Aguardando números sorteados...")
    
    atualizar_numeros()
    

if __name__ == "__main__":
    main()