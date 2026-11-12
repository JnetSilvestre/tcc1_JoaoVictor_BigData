from pon import *

def main():

    print("=== Teste da PON ===")

    # Criação dos atributos
    at1 = Attribute(0)
    at2 = Attribute(0)

    print("\nValores iniciais:")
    print("at1 =", at1.value)
    print("at2 =", at2.value)

    # Criação das premissas
    pr1 = at1 == at2
    pr2 = at1 != at2

    print("\nPremissas:")
    print("pr1 (at1 == at2) =", pr1.approved())
    print("pr2 (at1 != at2) =", pr2.approved())

    # Combinação das premissas
    cn1 = pr1 & pr2

    print("\nCondição:")
    print("cn1 (pr1 AND pr2) =", cn1.approved())

    # -------------------------------------------------
    # Teste 1
    # -------------------------------------------------

    print("\n=== Teste 1 ===")

    at1.value = 10

    print("at1 =", at1.value)
    print("at2 =", at2.value)

    print("pr1 (at1 == at2) =", pr1.approved())
    print("pr2 (at1 != at2) =", pr2.approved())
    print("cn1 (pr1 AND pr2) =", cn1.approved())

    # -------------------------------------------------
    # Teste 2
    # -------------------------------------------------

    print("\n=== Teste 2 ===")

    at2.value = 10

    print("at1 =", at1.value)
    print("at2 =", at2.value)

    print("pr1 (at1 == at2) =", pr1.approved())
    print("pr2 (at1 != at2) =", pr2.approved())
    print("cn1 (pr1 AND pr2) =", cn1.approved())


if __name__ == "__main__":
    main()