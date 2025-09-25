from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home / Upload
    path("", views.upload_file, name="upload"),

    # Resultado dos cálculos
    path("resultado/", views.resultado, name="resultado"),

    # Análise (stats + plotly)
    path("analise/", views.analysis, name="analysis"),

    # Relatório (download de PDF)
    path("relatorio/", views.relatorio, name="relatorio"),

    # Calculadora (manual + via NCM)
    path("calculadora/", views.calculadora, name="calculadora"),
]
