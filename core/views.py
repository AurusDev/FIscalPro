import os
from io import BytesIO

import pandas as pd
import plotly.express as px
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect

# ReportLab (PDF)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


# ==========
# Helpers
# ==========
def _get_session_file(request):
    """Retorna caminho do arquivo enviado, se existir e for válido."""
    file_path = request.session.get("uploaded_file")
    if file_path and os.path.exists(file_path):
        return file_path
    return None


def _compute_df(df: pd.DataFrame) -> pd.DataFrame:
    """Garante colunas mínimas e cria as colunas de cálculo."""
    required = ["UF", "NCM", "BASE_CALCULO", "ALIQ_ORIGEM", "ALIQ_DESTINO"]
    if not all(col in df.columns for col in required):
        faltando = [c for c in required if c not in df.columns]
        raise ValueError(f"Planilha sem colunas obrigatórias: {', '.join(faltando)}")

    df = df.copy()
    df["ICMS_ORIGEM"] = df["BASE_CALCULO"] * df["ALIQ_ORIGEM"]
    df["ICMS_DESTINO"] = df["BASE_CALCULO"] * df["ALIQ_DESTINO"]
    df["DIFAL"] = df["ICMS_DESTINO"] - df["ICMS_ORIGEM"]
    df["TOTAL_ICMS"] = df["ICMS_DESTINO"]
    return df


# ==========
# Views
# ==========
def upload_file(request):
    """
    Página inicial — upload do .xlsx.
    Salva o arquivo em MEDIA_ROOT/uploads e redireciona para 'resultado'.
    """
    if request.method == "POST" and request.FILES.get("file"):
        excel_file = request.FILES["file"]
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        fs = FileSystemStorage(location=upload_dir)
        filename = fs.save(excel_file.name, excel_file)
        request.session["uploaded_file"] = fs.path(filename)
        return redirect("resultado")

    return render(request, "upload.html")


def resultado(request):
    """
    Mostra a tabela calculada (mesma estética da análise).
    Somente aparece se houver planilha enviada.
    """
    file_path = _get_session_file(request)
    if not file_path:
        return redirect("upload")

    try:
        df = pd.read_excel(file_path)
        df = _compute_df(df)
    except Exception as e:
        return render(request, "resultado.html", {"error": f"Erro ao ler/processar planilha: {e}"})

    # Tabela bonita (mantendo o tema)
    table_html = df.to_html(
        classes="styled-table w-full text-sm text-center",
        index=False,
        border=0
    )

    return render(request, "resultado.html", {"table_html": table_html})


def analysis(request):
    """
    Estatísticas descritivas + 2 gráficos interativos (plotly).
    """
    file_path = _get_session_file(request)
    if not file_path:
        return redirect("upload")

    try:
        df = pd.read_excel(file_path)
        df = _compute_df(df)
    except Exception as e:
        return render(request, "analysis.html", {"error": f"Erro ao gerar análise: {e}"})

    # Stats
    stats_cols = [
        "BASE_CALCULO", "ALIQ_ORIGEM", "ALIQ_DESTINO",
        "ICMS_ORIGEM", "ICMS_DESTINO", "DIFAL", "TOTAL_ICMS"
    ]
    stats = df[stats_cols].describe().round(2)
    stats_html = stats.to_html(
        classes="styled-table w-full text-sm text-center",
        border=0, justify="center"
    )

    # Graf 1 — ICMS origem x destino por linha
    fig1 = px.bar(
        df.reset_index(),
        x="index",
        y=["ICMS_ORIGEM", "ICMS_DESTINO"],
        barmode="group",
        title="ICMS Origem vs Destino",
        labels={"index": "Linha"}
    )
    graph1 = fig1.to_html(full_html=False)

    # Graf 2 — Distribuição por UF
    fig2 = px.pie(
        df,
        names="UF",
        values="TOTAL_ICMS",
        title="Proporção do ICMS por UF"
    )
    graph2 = fig2.to_html(full_html=False)

    return render(
        request,
        "analysis.html",
        {"stats_html": stats_html, "graph1": graph1, "graph2": graph2},
    )


def relatorio(request):
    """
    Gera e baixa um PDF com a tabela calculada.
    """
    file_path = _get_session_file(request)
    if not file_path:
        return redirect("upload")

    try:
        df = pd.read_excel(file_path)
        df = _compute_df(df)
    except Exception as e:
        return render(request, "resultado.html", {"error": f"Erro ao gerar PDF: {e}"})

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("Relatório de Cálculo ICMS - PE", styles["Title"]),
        Spacer(1, 12),
    ]

    # Pequeno sumário
    try:
        linhas = len(df)
        base_total = float(df["BASE_CALCULO"].sum())
        icms_total = float(df["TOTAL_ICMS"].sum())
        resumo = Paragraph(
            f"Linhas: <b>{linhas}</b> &nbsp;&nbsp; "
            f"Base de Cálculo Total: <b>R$ {base_total:,.2f}</b> &nbsp;&nbsp; "
            f"Total ICMS: <b>R$ {icms_total:,.2f}</b>",
            styles["Normal"],
        )
        elements += [resumo, Spacer(1, 6)]
    except Exception:
        pass

    # Tabela
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5b21b6")),  # roxo
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#f5f3ff")]),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="relatorio_icms.pdf"'
    return response


def calculadora(request):
    resultado = None
    sugestao_origem, sugestao_destino = None, None
    df = None  # dataframe começa vazio

    # só tenta carregar se a chave realmente existir
    if request.session.get("uploaded_df"):
        try:
            df = pd.read_json(StringIO(request.session["uploaded_df"]))
        except Exception as e:
            print("Erro ao carregar planilha da sessão:", e)
            df = None

    if request.method == "POST":
        try:
            base_calculo = float(request.POST.get("base_calculo", 0))
            ncm = request.POST.get("ncm", "").strip()
            usar_ncm = request.POST.get("usar_ncm") == "on"

            # pega manual por padrão
            aliq_origem = float(request.POST.get("aliq_origem", 0)) / 100
            aliq_destino = float(request.POST.get("aliq_destino", 0)) / 100

            # se usar NCM e existir planilha carregada
            if usar_ncm and df is not None and ncm:
                if ncm in df["NCM"].astype(str).values:
                    row = df[df["NCM"].astype(str) == ncm].iloc[0]
                    aliq_origem = float(row["ALIQ_ORIGEM"])
                    aliq_destino = float(row["ALIQ_DESTINO"])
                    sugestao_origem = aliq_origem * 100
                    sugestao_destino = aliq_destino * 100

            # cálculo igual ao resto do app
            icms_origem = base_calculo * aliq_origem
            icms_destino = base_calculo * aliq_destino
            difal = icms_destino - icms_origem
            total_icms = icms_destino

            resultado = {
                "base": base_calculo,
                "ncm": ncm if ncm else "Manual",
                "aliq_origem": aliq_origem * 100,
                "aliq_destino": aliq_destino * 100,
                "icms_origem": round(icms_origem, 2),
                "icms_destino": round(icms_destino, 2),
                "difal": round(difal, 2),
                "total": round(total_icms, 2),
            }
        except Exception as e:
            resultado = {"erro": str(e)}

    return render(request, "calculadora.html", {
        "resultado": resultado,
        "sugestao_origem": sugestao_origem,
        "sugestao_destino": sugestao_destino,
    })
