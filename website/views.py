import matplotlib
matplotlib.use('Agg')  # Usar o backend correto
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import datetime, timedelta
from django.shortcuts import render

def index(request):
    # Gerar dados fictícios para previsão de demanda
    dates = [datetime.now() - timedelta(days=i) for i in range(30)]
    values = np.random.randint(50, 150, size=30)

    # Criar o gráfico
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(dates, values, marker='o', linestyle='-', color='blue')
    ax.set_title('Exemplo de Previsão de Demanda')
    ax.set_xlabel('Data')
    ax.set_ylabel('Demanda')
    plt.xticks(rotation=45)

    # Converter o gráfico em imagem para embutir no HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')

    # Passar o gráfico para o template
    context = {'graphic': graphic}
    return render(request, 'website/index.html', context)

# def forecast_view(request):
    # Gerar dados fictícios para previsão de demanda
    dates = [datetime.now() - timedelta(days=i) for i in range(30)]
    values = np.random.randint(50, 150, size=30)

    # Criar o gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, values, marker='o', linestyle='-', color='blue')
    ax.set_title('Exemplo de Previsão de Demanda')
    ax.set_xlabel('Data')
    ax.set_ylabel('Demanda')
    plt.xticks(rotation=45)

    # Converter o gráfico em imagem para embutir no HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')

    # Passar o gráfico para o template
    context = {'graphic': graphic}
    return render(request, 'website/index.html', context)