from pathlib import Path
import buildozer.targets.android as android_target

p = Path(android_target.__file__)

texto = p.read_text(
    encoding="utf-8"
)

flag = "--extra-manifest-application-xml"

print("Buildozer alvo:")
print(p)
print()

if flag in texto:
    print(
        "OK - Buildozer já possui suporte "
        "a --extra-manifest-application-xml"
    )
    raise SystemExit(0)


bloco = """        # support for extra-manifest-application-xml
        extra_manifest_application_xml = self.buildozer.config.get(
            'app',
            'android.extra_manifest_application_xml',
            fallback=''
        )
        if extra_manifest_application_xml:
            cmd.append(
                '--extra-manifest-application-xml'
            )
            cmd.append(
                '{}'.format(
                    open(
                        extra_manifest_application_xml,
                        'rt'
                    ).read()
                )
            )

"""


marcadores = [
    (
        "        # support for "
        "extra-manifest-application-arguments\n"
    ),
    (
        "        extra_manifest_application_arguments "
        "= self.buildozer.config.get(\n"
    ),
]


marcador_encontrado = None

for marcador in marcadores:

    if marcador in texto:
        marcador_encontrado = marcador
        break


if marcador_encontrado is None:

    raise SystemExit(
        "ERRO - Não encontrei o ponto onde "
        "o Buildozer trata "
        "extra-manifest-application-arguments."
    )


texto = texto.replace(
    marcador_encontrado,
    bloco + marcador_encontrado,
    1
)


p.write_text(
    texto,
    encoding="utf-8"
)


final = p.read_text(
    encoding="utf-8"
)


if flag not in final:

    raise SystemExit(
        "ERRO - patch não foi aplicado."
    )


print(
    "OK - Buildozer preparado para "
    "--extra-manifest-application-xml"
)
