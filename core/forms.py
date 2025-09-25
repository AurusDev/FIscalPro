from django import forms

class UploadForm(forms.Form):
    arquivo = forms.FileField(
        label="Envie a planilha (.xlsx)",
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx", "class": "block w-full"})
    )
