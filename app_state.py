import os
import json
from datetime import date

from devocionais_loader import carregar_devocional


TOTAL_DEVOCIONAIS = 40


class ProgressoDiscipulado:

    def __init__(self, pasta_dados):
        self.pasta_dados = pasta_dados
        os.makedirs(self.pasta_dados, exist_ok=True)

        self.arquivo = os.path.join(
            self.pasta_dados,
            "progresso.json"
        )

        self.dados = {
            "dia_automatico": 1,
            "ultimo_envio_automatico": 0,
            "data_ultimo_envio": ""
        }

        self.carregar()
        self.atualizar_dia_automatico()


    def carregar(self):

        if not os.path.exists(self.arquivo):
            self.salvar()
            return

        try:
            with open(
                self.arquivo,
                "r",
                encoding="utf-8"
            ) as f:
                dados_salvos = json.load(f)

            if isinstance(dados_salvos, dict):
                self.dados.update(dados_salvos)

        except Exception as erro:
            print(
                "Erro ao carregar progresso:",
                repr(erro)
            )

        self.validar()


    def validar(self):

        try:
            dia = int(
                self.dados.get(
                    "dia_automatico",
                    1
                )
            )
        except Exception:
            dia = 1

        dia = max(
            1,
            min(TOTAL_DEVOCIONAIS, dia)
        )

        self.dados["dia_automatico"] = dia

        try:
            ultimo = int(
                self.dados.get(
                    "ultimo_envio_automatico",
                    0
                )
            )
        except Exception:
            ultimo = 0

        self.dados[
            "ultimo_envio_automatico"
        ] = ultimo


    def salvar(self):

        try:
            with open(
                self.arquivo,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.dados,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        except Exception as erro:
            print(
                "Erro ao salvar progresso:",
                repr(erro)
            )


    def atualizar_dia_automatico(self):
        """
        Se o devocional automático foi enviado
        em um dia anterior, avança somente UM.

        Se vários dias passarem sem usar o app,
        nenhum devocional é pulado.
        """

        hoje = date.today().isoformat()

        dia_atual = self.dia_automatico()

        ultimo_enviado = int(
            self.dados.get(
                "ultimo_envio_automatico",
                0
            )
        )

        data_ultimo_envio = self.dados.get(
            "data_ultimo_envio",
            ""
        )

        if (
            data_ultimo_envio
            and data_ultimo_envio < hoje
            and ultimo_enviado == dia_atual
        ):

            if dia_atual < TOTAL_DEVOCIONAIS:

                self.dados[
                    "dia_automatico"
                ] = dia_atual + 1

                self.salvar()


    def dia_automatico(self):

        return int(
            self.dados.get(
                "dia_automatico",
                1
            )
        )


    def registrar_envio_automatico(
        self,
        dia
    ):
        """
        Só registra como envio automático
        quando o devocional enviado é exatamente
        o devocional automático atual.

        Um devocional escolhido manualmente
        não altera a sequência.
        """

        dia = int(dia)

        if dia != self.dia_automatico():
            return False

        self.dados[
            "ultimo_envio_automatico"
        ] = dia

        self.dados[
            "data_ultimo_envio"
        ] = date.today().isoformat()

        self.salvar()

        return True


    def reiniciar(self):

        self.dados = {
            "dia_automatico": 1,
            "ultimo_envio_automatico": 0,
            "data_ultimo_envio": ""
        }

        self.salvar()


def montar_mensagem(
    primeiro_nome,
    numero_devocional
):

    devocional = carregar_devocional(
        numero_devocional
    )

    dia = devocional["dia"]
    titulo = devocional["titulo"]
    conteudo = devocional["conteudo"]

    return f"""Graça e Paz, {primeiro_nome}! 🙏

🔥 *A FORJA DEVOCIONAL — DIA {dia}*

📖 *{titulo}*

{conteudo}

🔥 *Discipulador Cristão*"""
