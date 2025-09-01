from .jogada import JOGADAS

def analisar_regioes_quentes(numeros_analisados, quantidade_numeros):
    """
    Analisa quais estratégias (regiões) tiveram mais números sorteados
    dentro de uma quantidade de números específica.
    Retorna um dicionário com as contagens e a estratégia mais quente.
    """
    # Pega apenas a quantidade de números mais recentes para a análise
    # A lista é invertida para que o fatiamento pegue os números mais recentes.
    numeros_para_analise = numeros_analisados[::-1][:quantidade_numeros]
    
    contagens = {jogada.nome: 0 for jogada in JOGADAS.values()}
    
    for numero in numeros_para_analise:
        for jogada_nome, jogada_obj in JOGADAS.items():
            if jogada_obj.verificar(numero) == 'certo':
                contagens[jogada_nome] += 1
    
    # Encontra a região mais quente
    if contagens:
        regiao_mais_quente = max(contagens, key=contagens.get)
    else:
        regiao_mais_quente = "N/A"
        
    return contagens, regiao_mais_quente