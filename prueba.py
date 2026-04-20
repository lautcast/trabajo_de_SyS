import numpy as np
nombre  = "Laucha"


print(f"Mi nombre es {nombre}.")

def elevador(base:int, exponente:float) -> float:
    calculo = base**exponente
    return calculo

print(f"Tengo: {elevador(4,5.2)}")
print("Milito botón")
mi_señal = np.array([1, 2, 3, 4])