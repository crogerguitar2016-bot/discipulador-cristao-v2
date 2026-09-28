from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

from android_utils import (
    ler_contatos_android,
    solicitar_permissao_contatos,
    abrir_whatsapp_business,
    overlay_permitido,
    abrir_configuracao_overlay,
    iniciar_overlay_envio
)

from app_state import (
    ProgressoDiscipulado,
    montar_mensagem
)

from devocionais_loader import (
    carregar_devocional,
    carregar_todos
)


TOTAL_DEVOCIONAIS = 40


class DiscipuladorCristaoApp(App):

    title = "Discipulador Cristão V2"

    def build(self):

        self.contatos = []
        self.contato_selecionado = None

        # V2 - seleção múltipla
        self.contatos_selecionados = []
        self.botoes_contatos = []

        # Fila que será usada pelo controle flutuante
        self.fila_envio = []
        self.indice_fila = 0

        self.progresso = ProgressoDiscipulado(
            self.user_data_dir
        )

        self.dia_automatico = (
            self.progresso.dia_automatico()
        )

        self.dia_visualizado = (
            self.dia_automatico
        )

        # =================================================
        # LAYOUT PRINCIPAL
        # =================================================

        raiz = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            padding=dp(8)
        )

        # =================================================
        # CABEÇALHO
        # =================================================

        self.lbl_cabecalho = Label(
            text="[b]DISCIPULADOR CRISTÃO[/b]",
            markup=True,
            size_hint_y=None,
            height=dp(42),
            font_size="21sp"
        )

        raiz.add_widget(
            self.lbl_cabecalho
        )

        # =================================================
        # STATUS AUTOMÁTICO
        # =================================================

        self.lbl_status = Label(
            text="",
            markup=True,
            size_hint_y=None,
            height=dp(40),
            font_size="15sp"
        )

        raiz.add_widget(
            self.lbl_status
        )

        # =================================================
        # DIA E TÍTULO
        # =================================================

        self.lbl_dia = Label(
            text="",
            markup=True,
            size_hint_y=None,
            height=dp(34),
            font_size="18sp"
        )

        raiz.add_widget(
            self.lbl_dia
        )

        self.lbl_titulo = Label(
            text="",
            markup=True,
            size_hint_y=None,
            height=dp(55),
            font_size="17sp",
            halign="center",
            valign="middle"
        )

        self.lbl_titulo.bind(
            size=self._ajustar_texto
        )

        raiz.add_widget(
            self.lbl_titulo
        )

        # =================================================
        # TEXTO DO DEVOCIONAL
        # =================================================

        scroll_devocional = ScrollView(
            size_hint=(1, 0.38)
        )

        self.lbl_devocional = Label(
            text="",
            markup=False,
            size_hint_y=None,
            font_size="15sp",
            halign="left",
            valign="top",
            padding=(dp(8), dp(8))
        )

        self.lbl_devocional.bind(
            width=self._ajustar_largura_devocional
        )

        self.lbl_devocional.bind(
            texture_size=self._ajustar_altura_devocional
        )

        scroll_devocional.add_widget(
            self.lbl_devocional
        )

        raiz.add_widget(
            scroll_devocional
        )

        # =================================================
        # NAVEGAÇÃO
        # =================================================

        navegacao = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(5)
        )

        btn_anterior = Button(
            text="◀ ANTERIOR"
        )

        btn_escolher = Button(
            text="ESCOLHER"
        )

        btn_proximo = Button(
            text="PRÓXIMO ▶"
        )

        btn_anterior.bind(
            on_release=self.anterior
        )

        btn_escolher.bind(
            on_release=self.abrir_escolha_devocional
        )

        btn_proximo.bind(
            on_release=self.proximo
        )

        navegacao.add_widget(
            btn_anterior
        )

        navegacao.add_widget(
            btn_escolher
        )

        navegacao.add_widget(
            btn_proximo
        )

        raiz.add_widget(
            navegacao
        )

        # =================================================
        # VOLTAR AO AUTOMÁTICO
        # =================================================

        self.btn_hoje = Button(
            text="VOLTAR AO DEVOCIONAL DE HOJE",
            size_hint_y=None,
            height=dp(44)
        )

        self.btn_hoje.bind(
            on_release=self.voltar_ao_automatico
        )

        raiz.add_widget(
            self.btn_hoje
        )

        # =================================================
        # TÍTULO DOS CONTATOS
        # =================================================

        linha_contatos = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(5)
        )

        self.lbl_contatos = Label(
            text="[b]PESSOAS DO DISCIPULADO[/b]",
            markup=True
        )

        btn_atualizar = Button(
            text="ATUALIZAR",
            size_hint_x=0.35
        )

        btn_atualizar.bind(
            on_release=self.recarregar_contatos
        )

        linha_contatos.add_widget(
            self.lbl_contatos
        )

        linha_contatos.add_widget(
            btn_atualizar
        )

        raiz.add_widget(
            linha_contatos
        )

        # =================================================
        # SELEÇÃO MÚLTIPLA
        # =================================================

        linha_selecao = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(5)
        )

        btn_todos = Button(
            text="SELECIONAR TODOS"
        )

        btn_limpar = Button(
            text="LIMPAR"
        )

        btn_todos.bind(
            on_release=self.selecionar_todos
        )

        btn_limpar.bind(
            on_release=self.limpar_selecao
        )

        linha_selecao.add_widget(
            btn_todos
        )

        linha_selecao.add_widget(
            btn_limpar
        )

        raiz.add_widget(
            linha_selecao
        )

        # =================================================
        # LISTA DE CONTATOS
        # =================================================

        scroll_contatos = ScrollView(
            size_hint=(1, 0.25)
        )

        self.caixa_contatos = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None
        )

        self.caixa_contatos.bind(
            minimum_height=
            self.caixa_contatos.setter("height")
        )

        scroll_contatos.add_widget(
            self.caixa_contatos
        )

        raiz.add_widget(
            scroll_contatos
        )

        # =================================================
        # RESUMO DA SELEÇÃO
        # =================================================

        self.lbl_selecionado = Label(
            text="Nenhuma pessoa selecionada.",
            size_hint_y=None,
            height=dp(34),
            font_size="14sp"
        )

        raiz.add_widget(
            self.lbl_selecionado
        )

        # =================================================
        # INICIAR ENVIO
        # =================================================

        self.btn_enviar = Button(
            text="INICIAR ENVIO",
            size_hint_y=None,
            height=dp(55),
            font_size="19sp",
            disabled=True
        )

        self.btn_enviar.bind(
            on_release=self.enviar
        )

        raiz.add_widget(
            self.btn_enviar
        )

        # =================================================
        # PRIMEIRA ATUALIZAÇÃO
        # =================================================

        self.atualizar_devocional()

        Clock.schedule_once(
            self.iniciar_contatos,
            0.8
        )

        return raiz


    # =====================================================
    # AJUSTES DE TEXTO
    # =====================================================

    def _ajustar_texto(
        self,
        widget,
        tamanho
    ):

        widget.text_size = (
            tamanho[0] - dp(12),
            None
        )


    def _ajustar_largura_devocional(
        self,
        widget,
        largura
    ):

        widget.text_size = (
            largura - dp(20),
            None
        )


    def _ajustar_altura_devocional(
        self,
        widget,
        textura
    ):

        widget.height = (
            textura[1] + dp(20)
        )


    # =====================================================
    # DEVOCIONAL ATUAL
    # =====================================================

    def atualizar_devocional(self):

        devocional = carregar_devocional(
            self.dia_visualizado
        )

        self.lbl_dia.text = (
            f"[b]DIA {devocional['dia']}[/b]"
        )

        self.lbl_titulo.text = (
            f"[b]{devocional['titulo']}[/b]"
        )

        self.lbl_devocional.text = (
            devocional["conteudo"]
        )

        if (
            self.dia_visualizado
            == self.dia_automatico
        ):

            self.lbl_status.text = (
                "[b]🟢 DEVOCIONAL AUTOMÁTICO DE HOJE[/b]"
            )

            self.btn_hoje.disabled = True

        else:

            self.lbl_status.text = (
                "[b]🟡 DEVOCIONAL ESCOLHIDO MANUALMENTE[/b]"
            )

            self.btn_hoje.disabled = False


    # =====================================================
    # ANTERIOR
    # =====================================================

    def anterior(self, *args):

        if self.dia_visualizado > 1:

            self.dia_visualizado -= 1

            self.atualizar_devocional()


    # =====================================================
    # PRÓXIMO
    # =====================================================

    def proximo(self, *args):

        if (
            self.dia_visualizado
            < TOTAL_DEVOCIONAIS
        ):

            self.dia_visualizado += 1

            self.atualizar_devocional()


    # =====================================================
    # VOLTAR AO AUTOMÁTICO
    # =====================================================

    def voltar_ao_automatico(
        self,
        *args
    ):

        self.dia_visualizado = (
            self.dia_automatico
        )

        self.atualizar_devocional()


    # =====================================================
    # ESCOLHER QUALQUER DEVOCIONAL
    # =====================================================

    def abrir_escolha_devocional(
        self,
        *args
    ):

        conteudo = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(5)
        )

        scroll = ScrollView()

        lista = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None
        )

        lista.bind(
            minimum_height=
            lista.setter("height")
        )

        todos = carregar_todos()

        popup = Popup(
            title="Escolher Devocional",
            size_hint=(0.94, 0.88)
        )

        for devocional in todos:

            numero = devocional["dia"]

            titulo = devocional["titulo"]

            botao = Button(
                text=(
                    f"{numero:02d} - "
                    f"{titulo}"
                ),
                size_hint_y=None,
                height=dp(48)
            )

            botao.bind(
                on_release=lambda btn,
                n=numero,
                p=popup:
                self.selecionar_devocional(
                    n,
                    p
                )
            )

            lista.add_widget(
                botao
            )

        scroll.add_widget(
            lista
        )

        conteudo.add_widget(
            scroll
        )

        popup.content = conteudo

        popup.open()


    def selecionar_devocional(
        self,
        numero,
        popup
    ):

        self.dia_visualizado = int(
            numero
        )

        popup.dismiss()

        self.atualizar_devocional()


    # =====================================================
    # CONTATOS
    # =====================================================

    def iniciar_contatos(
        self,
        *args
    ):

        self.lbl_contatos.text = (
            "[b]Solicitando acesso aos contatos...[/b]"
        )

        solicitar_permissao_contatos(
            self.permissao_respondida
        )


    def permissao_respondida(
        self,
        permitido
    ):

        if permitido:

            Clock.schedule_once(
                self.carregar_contatos,
                0.3
            )

        else:

            self.lbl_contatos.text = (
                "[b]Permissão de contatos não concedida[/b]"
            )


    def recarregar_contatos(
        self,
        *args
    ):

        solicitar_permissao_contatos(
            self.permissao_respondida
        )


    def carregar_contatos(
        self,
        *args
    ):

        self.lbl_contatos.text = (
            "[b]Carregando contatos...[/b]"
        )

        # Mantém selecionados que ainda existirem
        # depois de uma atualização da agenda.
        numeros_selecionados = {
            contato["numero"]
            for contato in self.contatos_selecionados
        }

        self.caixa_contatos.clear_widgets()

        self.contatos = (
            ler_contatos_android()
        )

        self.contatos_selecionados = []
        self.botoes_contatos = []

        if not self.contatos:

            self.lbl_contatos.text = (
                "[b]Nenhum contato "
                "Koinonia Discipulado encontrado[/b]"
            )

            self._atualizar_resumo_selecao()
            return

        self.lbl_contatos.text = (
            f"[b]PESSOAS DO DISCIPULADO "
            f"({len(self.contatos)})[/b]"
        )

        for indice, contato in enumerate(
            self.contatos,
            start=1
        ):

            nome = contato[
                "primeiro_nome"
            ]

            botao = ToggleButton(
                text=f"[ ] {indice} - {nome}",
                size_hint_y=None,
                height=dp(44)
            )

            botao.texto_base = (
                f"{indice} - {nome}"
            )

            if (
                contato["numero"]
                in numeros_selecionados
            ):

                botao.state = "down"
                botao.text = (
                    f"[X] {botao.texto_base}"
                )

                self.contatos_selecionados.append(
                    contato
                )

            botao.bind(
                on_release=lambda btn,
                c=contato:
                self.selecionar_contato(
                    c,
                    btn
                )
            )

            self.botoes_contatos.append(
                (botao, contato)
            )

            self.caixa_contatos.add_widget(
                botao
            )

        self._atualizar_resumo_selecao()


    def selecionar_contato(
        self,
        contato,
        botao
    ):

        if botao.state == "down":

            if (
                contato
                not in self.contatos_selecionados
            ):

                self.contatos_selecionados.append(
                    contato
                )

            botao.text = (
                f"[X] {botao.texto_base}"
            )

        else:

            if (
                contato
                in self.contatos_selecionados
            ):

                self.contatos_selecionados.remove(
                    contato
                )

            botao.text = (
                f"[ ] {botao.texto_base}"
            )

        self._atualizar_resumo_selecao()


    def selecionar_todos(
        self,
        *args
    ):

        self.contatos_selecionados = list(
            self.contatos
        )

        for botao, contato in self.botoes_contatos:

            botao.state = "down"
            botao.text = (
                f"[X] {botao.texto_base}"
            )

        self._atualizar_resumo_selecao()


    def limpar_selecao(
        self,
        *args
    ):

        self.contatos_selecionados = []

        for botao, contato in self.botoes_contatos:

            botao.state = "normal"
            botao.text = (
                f"[ ] {botao.texto_base}"
            )

        self._atualizar_resumo_selecao()


    def _atualizar_resumo_selecao(
        self
    ):

        quantidade = len(
            self.contatos_selecionados
        )

        if quantidade == 0:

            self.lbl_selecionado.text = (
                "Nenhuma pessoa selecionada."
            )

            self.btn_enviar.disabled = True

        elif quantidade == 1:

            nome = (
                self.contatos_selecionados[0]
                ["primeiro_nome"]
            )

            self.lbl_selecionado.text = (
                f"1 pessoa selecionada: {nome}"
            )

            self.btn_enviar.disabled = False

        else:

            self.lbl_selecionado.text = (
                f"{quantidade} pessoas selecionadas"
            )

            self.btn_enviar.disabled = False


    # =====================================================
    # ENVIAR
    # =====================================================

    def enviar(
        self,
        *args
    ):

        if not self.contatos_selecionados:
            return

        # ==================================================
        # PREPARAR FILA PERSONALIZADA
        # ==================================================

        self.fila_envio = []

        for pessoa in self.contatos_selecionados:

            nome = pessoa[
                "primeiro_nome"
            ]

            mensagem = montar_mensagem(
                nome,
                self.dia_visualizado
            )

            self.fila_envio.append({
                "nome": nome,
                "numero": pessoa["numero"],
                "mensagem": mensagem
            })


        # ==================================================
        # PRIMEIRA VEZ:
        # PEDIR PERMISSÃO PARA JANELA FLUTUANTE
        # ==================================================

        if not overlay_permitido():

            sucesso, erro = (
                abrir_configuracao_overlay()
            )

            if sucesso:

                self.lbl_selecionado.text = (
                    "Autorize 'Exibir sobre outros apps'. "
                    "Depois volte e toque "
                    "INICIAR ENVIO novamente."
                )

            else:

                self.mostrar_erro(
                    erro
                )

            return


        # ==================================================
        # INICIAR JANELA FLUTUANTE + WHATSAPP
        # ==================================================

        sucesso, erro = (
            iniciar_overlay_envio(
                self.fila_envio
            )
        )

        if sucesso:

            quantidade = len(
                self.fila_envio
            )

            self.lbl_selecionado.text = (
                f"Fila iniciada: "
                f"{quantidade} pessoa(s)"
            )

            # O próprio OverlayService abrirá
            # o primeiro contato no WhatsApp Business.
            #
            # Depois:
            #
            #   ANTERIOR
            #   PRÓXIMO
            #   ENCERRAR ENVIO
            #
            # funcionarão diretamente sobre o WhatsApp.

            if (
                self.dia_visualizado
                == self.dia_automatico
            ):

                self.progresso.registrar_envio_automatico(
                    self.dia_visualizado
                )

        else:

            self.mostrar_erro(
                erro
            )



    # =====================================================
    # ERRO
    # =====================================================

    def mostrar_erro(
        self,
        mensagem
    ):

        caixa = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        texto = Label(
            text=str(mensagem),
            halign="center",
            valign="middle"
        )

        texto.bind(
            size=lambda w, s:
            setattr(
                w,
                "text_size",
                (s[0], None)
            )
        )

        btn = Button(
            text="OK",
            size_hint_y=None,
            height=dp(45)
        )

        caixa.add_widget(
            texto
        )

        caixa.add_widget(
            btn
        )

        popup = Popup(
            title="Discipulador Cristão",
            content=caixa,
            size_hint=(0.88, 0.45)
        )

        btn.bind(
            on_release=popup.dismiss
        )

        popup.open()


if __name__ == "__main__":
    DiscipuladorCristaoApp().run()
