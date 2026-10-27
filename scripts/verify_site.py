"""Verify the main HTTP resources and save the result as evidence."""

import re
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "verificacion_http.txt"

URLS = [
    "/",
    "/article/tecsup-inaugura-laboratorio-inteligencia-artificial/",
    "/category/tecnologia/",
    "/static/css/styles.css",
    "/media/articles/tecsup-inaugura-laboratorio-inteligencia-artificial.jpg",
]


def main():
    lines = [
        "Verificación HTTP del portal - Laboratorio 06",
        "=" * 55,
        f"Base URL: {BASE_URL}",
        "",
        f"{'Recurso':<90} {'HTTP':<6} Content-Type",
        "-" * 130,
    ]
    home_html = ""
    for path in URLS:
        try:
            with urllib.request.urlopen(BASE_URL + path) as response:
                body = response.read()
                content_type = response.headers.get("Content-Type", "")
                status = response.status
                if path == "/":
                    home_html = body.decode("utf-8")
        except urllib.error.HTTPError as error:
            status = error.code
            content_type = error.headers.get("Content-Type", "")
        lines.append(f"{path:<90} {status:<6} {content_type}")

    if home_html:
        lines.extend(
            [
                "",
                "Comprobaciones sobre la portada:",
                f"- Tarjetas article-card: {len(re.findall('class="article-card"', home_html))}",
                f"- Imágenes /media/articles/: {len(re.findall('/media/articles/', home_html))}",
                f"- Hoja de estilos enlazada: {'/static/css/styles.css' in home_html}",
                f"- Enlaces a /article/: {len(re.findall('href="/article/', home_html))}",
                f"- Enlaces a /category/: {len(re.findall('href="/category/', home_html))}",
            ]
        )

    report = "\n".join(lines) + "\n"
    OUTPUT.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
