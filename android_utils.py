import re
import unicodedata
import urllib.parse


PALAVRA_1 = "koinonia"
PALAVRA_2 = "discipulado"


def normalizar(texto):
    texto = str(texto or "")
    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    return texto.casefold().strip()


def primeiro_nome(nome_completo):
    partes = str(nome_completo or "").strip().split()

    # Procura o primeiro nome que não seja
    # um dos marcadores do sistema.
    for parte in partes:
        p = normalizar(parte)

        if p not in (PALAVRA_1, PALAVRA_2):
            return parte

    return partes[0] if partes else ""


def contato_eh_discipulado(nome):
    nome_normalizado = normalizar(nome)

    tem_koinonia = re.search(
        r"\bkoinonia\b",
        nome_normalizado
    )

    tem_discipulado = re.search(
        r"\bdiscipulado\b",
        nome_normalizado
    )

    return bool(tem_koinonia and tem_discipulado)


def limpar_numero(numero):
    numero = re.sub(
        r"\D",
        "",
        str(numero or "")
    )

    # Remove zero inicial, se houver.
    while numero.startswith("0"):
        numero = numero[1:]

    # Para números brasileiros armazenados
    # apenas com DDD + telefone.
    if len(numero) in (10, 11):
        numero = "55" + numero

    return numero


def ordenar_e_remover_duplicados(contatos):
    resultado = []
    vistos = set()

    for contato in contatos:

        nome = contato.get("nome", "").strip()
        numero = limpar_numero(
            contato.get("numero", "")
        )

        if not nome or not numero:
            continue

        if not contato_eh_discipulado(nome):
            continue

        chave = (
            normalizar(nome),
            numero
        )

        if chave in vistos:
            continue

        vistos.add(chave)

        resultado.append({
            "nome": nome,
            "primeiro_nome": primeiro_nome(nome),
            "numero": numero
        })

    resultado.sort(
        key=lambda item: normalizar(
            item["primeiro_nome"]
        )
    )

    return resultado


def ler_contatos_android():
    """
    Lê diretamente os contatos do Android.

    Retorna somente contatos cujo nome contenha:
    Koinonia + Discipulado.
    """

    try:
        from kivy.utils import platform

        if platform != "android":
            return []

        from jnius import autoclass

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        Phone = autoclass(
            "android.provider.ContactsContract"
            "$CommonDataKinds$Phone"
        )

        activity = PythonActivity.mActivity
        resolver = activity.getContentResolver()

        cursor = resolver.query(
            Phone.CONTENT_URI,
            None,
            None,
            None,
            "display_name COLLATE NOCASE ASC"
        )

        encontrados = []

        if cursor is None:
            return []

        indice_nome = cursor.getColumnIndex(
            Phone.DISPLAY_NAME
        )

        indice_numero = cursor.getColumnIndex(
            Phone.NUMBER
        )

        while cursor.moveToNext():

            nome = cursor.getString(
                indice_nome
            )

            numero = cursor.getString(
                indice_numero
            )

            if contato_eh_discipulado(nome):

                encontrados.append({
                    "nome": nome,
                    "numero": numero
                })

        cursor.close()

        return ordenar_e_remover_duplicados(
            encontrados
        )

    except Exception as erro:
        print(
            "Erro ao ler contatos:",
            repr(erro)
        )

        return []


def solicitar_permissao_contatos(callback=None):
    """
    Solicita READ_CONTACTS em tempo de execução.
    """

    try:
        from kivy.utils import platform

        if platform != "android":

            if callback:
                callback(False)

            return

        from android.permissions import (
            Permission,
            check_permission,
            request_permissions
        )

        if check_permission(
            Permission.READ_CONTACTS
        ):

            if callback:
                callback(True)

            return

        def retorno(permissoes, resultados):

            permitido = bool(
                resultados
                and all(resultados)
            )

            if callback:
                callback(permitido)

        request_permissions(
            [Permission.READ_CONTACTS],
            retorno
        )

    except Exception as erro:

        print(
            "Erro ao solicitar permissão:",
            repr(erro)
        )

        if callback:
            callback(False)


def abrir_whatsapp_business(numero, mensagem):
    """
    Abre uma conversa no WhatsApp Business
    com a mensagem já preenchida.
    """

    numero = limpar_numero(numero)

    if not numero:
        return False, "Número inválido."

    try:
        from kivy.utils import platform

        if platform != "android":
            return False, "Função disponível somente no Android."

        from jnius import autoclass

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        Intent = autoclass(
            "android.content.Intent"
        )

        Uri = autoclass(
            "android.net.Uri"
        )

        activity = PythonActivity.mActivity

        texto = urllib.parse.quote(
            mensagem,
            safe=""
        )

        url = (
            "whatsapp://send"
            f"?phone={numero}"
            f"&text={texto}"
        )

        intent = Intent(
            Intent.ACTION_VIEW,
            Uri.parse(url)
        )

        # WhatsApp Business
        intent.setPackage(
            "com.whatsapp.w4b"
        )

        activity.startActivity(intent)

        return True, ""

    except Exception as erro:

        return (
            False,
            "Não foi possível abrir o "
            "WhatsApp Business.\n\n"
            + str(erro)
        )



# ==========================================================
# JANELA FLUTUANTE / OVERLAY - DISCIPULADOR CRISTÃO V2
# ==========================================================

def overlay_permitido():
    """
    Verifica se o Android autorizou o aplicativo
    a aparecer sobre outros aplicativos.
    """

    try:
        from kivy.utils import platform

        if platform != "android":
            return False

        from jnius import autoclass

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        Settings = autoclass(
            "android.provider.Settings"
        )

        BuildVersion = autoclass(
            "android.os.Build$VERSION"
        )

        activity = PythonActivity.mActivity

        # Antes do Android 6 a permissão especial
        # de overlay não precisava ser concedida
        # pela tela de configurações.
        if BuildVersion.SDK_INT < 23:
            return True

        return bool(
            Settings.canDrawOverlays(
                activity
            )
        )

    except Exception as erro:

        print(
            "Erro ao verificar overlay:",
            repr(erro)
        )

        return False


def abrir_configuracao_overlay():
    """
    Abre a configuração Android:
    'Exibir sobre outros apps'.
    """

    try:
        from kivy.utils import platform

        if platform != "android":

            return (
                False,
                "Função disponível somente no Android."
            )

        if overlay_permitido():

            return True, ""

        from jnius import autoclass

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        Intent = autoclass(
            "android.content.Intent"
        )

        Settings = autoclass(
            "android.provider.Settings"
        )

        Uri = autoclass(
            "android.net.Uri"
        )

        activity = PythonActivity.mActivity

        pacote = str(
            activity.getPackageName()
        )

        intent = Intent(
            Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
            Uri.parse(
                "package:" + pacote
            )
        )

        activity.startActivity(
            intent
        )

        return True, ""

    except Exception as erro:

        return (
            False,
            "Não foi possível abrir a permissão "
            "'Exibir sobre outros apps'.\n\n"
            + str(erro)
        )


def iniciar_overlay_envio(fila):
    """
    Inicia o serviço nativo OverlayService.

    fila:
    [
        {
            "nome": "...",
            "numero": "...",
            "mensagem": "..."
        }
    ]
    """

    try:
        from kivy.utils import platform

        if platform != "android":

            return (
                False,
                "Função disponível somente no Android."
            )

        if not overlay_permitido():

            return (
                False,
                "A permissão para exibir sobre "
                "outros aplicativos ainda não foi concedida."
            )

        import json

        from jnius import autoclass

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        Intent = autoclass(
            "android.content.Intent"
        )

        activity = PythonActivity.mActivity

        fila_limpa = []

        for pessoa in fila:

            numero = limpar_numero(
                pessoa.get(
                    "numero",
                    ""
                )
            )

            if not numero:
                continue

            fila_limpa.append({
                "nome": str(
                    pessoa.get(
                        "nome",
                        ""
                    )
                ),

                "numero": numero,

                "mensagem": str(
                    pessoa.get(
                        "mensagem",
                        ""
                    )
                )
            })

        if not fila_limpa:

            return (
                False,
                "Nenhum número válido encontrado."
            )

        dados_json = json.dumps(
            fila_limpa,
            ensure_ascii=False
        )

        intent = Intent()

        pacote = str(
            activity.getPackageName()
        )

        intent.setClassName(
            pacote,
            "com.croger.discipuladorcristaov2.OverlayService"
        )

        intent.putExtra(
            "fila_json",
            dados_json
        )

        # O serviço é iniciado enquanto o
        # Discipulador ainda está em primeiro plano.
        activity.startService(
            intent
        )

        return True, ""

    except Exception as erro:

        return (
            False,
            "Não foi possível iniciar a janela "
            "flutuante.\n\n"
            + str(erro)
        )
