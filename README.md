# ⚡ FiscalPro

**FiscalPro** é uma aplicação web desenvolvida em **Django** para auxiliar no cálculo do **ICMS** e geração de relatórios fiscais.  
Com ele você pode:

✅ Fazer upload de planilhas Excel (.xlsx)  
✅ Calcular automaticamente ICMS de origem, destino e DIFAL  
✅ Visualizar análises interativas de dados  
✅ Usar uma calculadora manual de ICMS  
✅ Exportar relatórios para uso prático no dia a dia  

---

## 📸 Preview
![Preview da aplicação](docs/preview.png)  
*(adicione uma imagem da tela principal do sistema aqui)*

---

## 🚀 Tecnologias Utilizadas
- [Python 3.13+](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)
- [Bootstrap + TailwindCSS](https://tailwindcss.com/) (UI moderna)
- Deploy com [Render](https://render.com/) ou [Railway](https://railway.app/)

---

## ⚙️ Instalação Local

1) Clone este repositório:
```bash
git clone https://github.com/AurusDev/FiscalPro.git
cd FiscalPro
```

2) Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3) Instale as dependências:
```bash
pip install -r requirements.txt
```

4) Execute as migrações do banco:
```bash
python manage.py migrate
```

5) Inicie o servidor:
```bash
python manage.py runserver
```

6) Acesse em: http://127.0.0.1:8000/ 🎉

---

## 📊 Funcionalidades
- 📂 Upload de planilhas Excel
- 🧮 Calculadora de ICMS manual
- 📈 Análise de dados com gráficos interativos
- 📑 Relatórios organizados
- 🌐 Deploy em cloud (Render/Railway)
