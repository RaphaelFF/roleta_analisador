import streamlit as st
from streamlit_autorefresh import st_autorefresh
from modules.jogada import JOGADAS
from modules.cores import aplicar_cor_especial, formatar_numero

st.set_page_config(layout="wide")

if 'numeros_sorteados' not in st.session_state:
    st.session_state.numeros_sorteados = []
if 'linhas_processadas' not in st.session_state:
    st.session_state.linhas_processadas = 0

# A cada 2 segundos, a função adiciona_ultimos_numeros será executada
st_autorefresh(interval=2000, key="auto_refresh")

def adicionar_ultimos_numeros():
    try:
        with open('resultados_roleta.txt', 'r') as f:
            linhas = f.readlines()
            total_linhas = len(linhas)
            
            # Compara o número total de linhas do arquivo com as que já processamos
            if total_linhas > st.session_state.linhas_processadas:
                # Itera apenas sobre as novas linhas que ainda não foram processadas
                for linha in linhas[st.session_state.linhas_processadas:]:
                    linha_limpa = linha.strip()
                    if linha_limpa:
                        try:
                            novo_numero = int(linha_limpa)
                            st.session_state.numeros_sorteados.append(novo_numero)
                        except ValueError:
                            # Ignora linhas que não são números válidos
                            pass
                
                # Atualiza a contagem de linhas processadas
                st.session_state.linhas_processadas = total_linhas
                
                
    except FileNotFoundError:
        st.warning("Arquivo 'resultados.txt' não encontrado. Certifique-se de que o web scraper está rodando.")
        pass

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
    jogada_selecionada_obj = JOGADAS[st.session_state.jogada_selecionada]
    status = jogada_selecionada_obj.verificar(numero)
    
    cor_especial = aplicar_cor_especial(
        numero, status, jogada_selecionada_obj.verificar,
        st.session_state.numeros_sorteados, indice_original,
        st.session_state.sequencias_consecutivas,
        st.session_state.inverter_logica,
        st.session_state.inverter_logica_sequencia
    )
    
    if cor_especial:
        cor, num = cor_especial
        col.markdown(formatar_numero(num, cor), unsafe_allow_html=True)
    else:
        col.markdown(formatar_numero(numero, status), unsafe_allow_html=True)

def main():
    
    st.title('Análise de Padrões na Roleta Europeia')
    
    with st.sidebar:
        st.header("Configurações da Análise")
        st.session_state.jogada_selecionada = st.selectbox('Selecione a Estratégia:', list(JOGADAS.keys()))
        st.session_state.sequencias_consecutivas = st.slider('Sequências consecutivas para análise', min_value=2, max_value=5, value=3)
        st.session_state.inverter_logica_sequencia = st.checkbox('Analisar sequências de "erros"', help="Verifica sequências consecutivas de números que *não* fazem parte da estratégia escolhida.")
        st.session_state.inverter_logica = st.checkbox('Analisar quebra de sequência', help="Ex: Se a estratégia for 3 acertos, a quebra acontece em 2 acertos + 1 erro.")
        
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
    
    with st.container():
        
        if st.session_state.numeros_sorteados:
            num_colunas_exibicao = 8
            numeros_invertidos = st.session_state.numeros_sorteados[::-1]
            
            cols = st.columns(num_colunas_exibicao)
            
            for i, numero in enumerate(numeros_invertidos):
                render_numero(cols[i % num_colunas_exibicao], numero, i)
        else:
            st.info("Aguardando números sorteados...")
    
        adicionar_ultimos_numeros()

if __name__ == "__main__":
    main()