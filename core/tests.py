from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .services.pipeline import run_pipeline
import pandas as pd

class PipelineTests(TestCase):
    def test_pipeline_basico(self):
        # cria planilha fake em memória
        df = pd.DataFrame({
            "BASE_CALCULO": [100, 200],
            "ALIQ_ORIGEM": [0.07, 0.12],
            "ALIQ_DESTINO": [0.18, 0.18]
        })
        file = SimpleUploadedFile("teste.xlsx", df.to_excel(index=False).encode(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        result = run_pipeline(file)
        self.assertIn("DIFAL", result.columns)
