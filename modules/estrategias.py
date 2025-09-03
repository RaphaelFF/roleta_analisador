# A classe que define o comportamento de uma jogada
class Jogada:
    def __init__(self, nome, numeros_alvo, numeros_especiais):
        self.nome = nome
        self.numeros_alvo = set(numeros_alvo)
        self.numeros_especiais = set(numeros_especiais)

    def verificar(self, numero):
        """Verifica se o número pertence ao conjunto de números-alvo da jogada."""
        return 'certo' if numero in self.numeros_alvo else 'errado'

    def eh_especial(self, numero):
        """Verifica se o número é um dos números especiais da jogada."""
        return numero in self.numeros_especiais

# Dicionário com as instâncias de cada jogada
JOGADAS = {
    "Vizinho 34": Jogada(
        "Vizinho 34",
        {0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10},
        {}
    ),
    "Vizinho 22": Jogada(
        "Vizinho 22",
        {0, 26, 3, 35, 12, 28, 7, 29, 18, 22, 9, 31, 14, 20, 1, 33, 16, 24, 5},
        {}
    ),
    "Vizinho 23": Jogada(
        "Vizinho 23",
        {31, 14, 20, 1, 33, 16, 24, 5, 10, 23, 8, 30, 11, 36, 13, 27, 6, 34, 17},
        {}
    ),
    "Vizinho 0": Jogada(
        "Vizinho 0",
        {34, 17, 25, 2, 21, 4, 19, 15, 32, 0, 26, 3, 35, 12, 28, 7, 29, 18, 22},
        {}
    )
}