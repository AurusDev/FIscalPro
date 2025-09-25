from django.db import models

# Por enquanto não usamos banco, apenas sessão
# Mas aqui podemos guardar histórico de uploads ou resultados no futuro
class UploadHistorico(models.Model):
    nome_arquivo = models.CharField(max_length=255)
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_arquivo
