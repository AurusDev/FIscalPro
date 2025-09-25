import io
import pandas as pd

def run_pipeline(file_obj) -> pd.DataFrame:
    """
    Lê a planilha enviada e executa um cálculo ICMS básico (exemplo).
    Espera abas:
      - Entradas (BASE_CALCULO, ALIQ_ORIGEM, ALIQ_DESTINO, UF, NCM)
      - Parametros (opcional) para enriquecimento por UF/NCM
    """
    # aceita InMemoryUploadedFile/TemporaryUploadedFile/BytesIO
    if hasattr(file_obj, "read"):
        data = file_obj.read()
        file_like = io.BytesIO(data)
    else:
        file_like = file_obj

    # tenta ler múltiplas abas
    xl = pd.ExcelFile(file_like)
    if "Entradas" in xl.sheet_names:
        df = xl.parse("Entradas")
    else:
        # fallback: primeira aba
        df = xl.parse(xl.sheet_names[0])

    # normaliza colunas
    cols = {c: c.strip().upper() for c in df.columns}
    df.rename(columns=cols, inplace=True)

    for needed in ["BASE_CALCULO", "ALIQ_ORIGEM", "ALIQ_DESTINO"]:
        if needed not in df.columns:
            df[needed] = 0

    # garante formatos
    df["BASE_CALCULO"] = pd.to_numeric(df["BASE_CALCULO"], errors="coerce").fillna(0.0)
    df["ALIQ_ORIGEM"] = pd.to_numeric(df["ALIQ_ORIGEM"], errors="coerce").fillna(0.0)
    df["ALIQ_DESTINO"] = pd.to_numeric(df["ALIQ_DESTINO"], errors="coerce").fillna(0.0)

    # cálculo DIFAL simples = base * (aliq_dest - aliq_orig)
    df["DIFAL"] = df["BASE_CALCULO"] * (df["ALIQ_DESTINO"] - df["ALIQ_ORIGEM"])
    df["DIFAL"] = df["DIFAL"].round(2)

    # calcula ICMS de origem e destino (exemplo)
    df["ICMS_ORIGEM"] = (df["BASE_CALCULO"] * df["ALIQ_ORIGEM"]).round(2)
    df["ICMS_DESTINO"] = (df["BASE_CALCULO"] * df["ALIQ_DESTINO"]).round(2)

    # total
    df["TOTAL_ICMS"] = (df["ICMS_ORIGEM"] + df["DIFAL"]).round(2)

    # reordena se existirem UF/NCM
    order = [c for c in ["UF", "NCM", "BASE_CALCULO", "ALIQ_ORIGEM", "ALIQ_DESTINO",
                         "ICMS_ORIGEM", "DIFAL", "ICMS_DESTINO", "TOTAL_ICMS"] if c in df.columns]
    df = df[order + [c for c in df.columns if c not in order]]

    return df
