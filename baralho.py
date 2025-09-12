# Funções relacionadas ao estudo de baralhos

import random

def embaralhar_cartas(cartas):
    cartas_copy = list(cartas)
    random.shuffle(cartas_copy)
    return cartas_copy

def selecionar_cartas(cartas, quantidade):
    return cartas[:quantidade]