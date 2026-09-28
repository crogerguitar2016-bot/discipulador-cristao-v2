import os


def pasta_do_app():
    return os.path.dirname(
        os.path.abspath(__file__)
    )


def carregar_devocional(numero):
    numero = int(numero)

    caminho = os.path.join(
        pasta_do_app(),
        "devocionais",
        f"{numero:02d}.txt"
    )

    if not os.path.exists(caminho):
        return {
            "dia": numero,
            "titulo": f"Dia {numero}",
            "conteudo": "Devocional ainda não disponível."
        }

    with open(
        caminho,
        "r",
        encoding="utf-8"
    ) as arquivo:
        texto = arquivo.read().strip()

    linhas = texto.splitlines()

    titulo = f"Dia {numero}"

    if linhas:
        primeira = linhas[0].strip()

        if primeira.startswith("TITULO="):
            titulo = primeira.split(
                "=",
                1
            )[1].strip()

            conteudo = "\n".join(
                linhas[1:]
            ).strip()

        else:
            conteudo = texto

    else:
        conteudo = ""

    return {
        "dia": numero,
        "titulo": titulo,
        "conteudo": conteudo
    }


def carregar_todos():
    return [
        carregar_devocional(numero)
        for numero in range(1, 41)
    ]
