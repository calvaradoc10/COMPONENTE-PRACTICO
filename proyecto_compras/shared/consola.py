def imprimir_titulo(texto):
    print("\n" + "=" * 54)
    print(f" {texto}")
    print("=" * 54)

def imprimir_exito(texto):
    print(f"\n[OK] {texto}")

def imprimir_error(texto):
    print(f"\n[ERROR] {texto}")

def imprimir_info(texto):
    print(f"\n{texto}")

def confirmar(texto="¿Está seguro? (s/n): "):
    return input(texto).strip().lower() in ("s", "si", "sí", "y", "yes")
