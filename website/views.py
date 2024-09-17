import matplotlib
matplotlib.use('Agg')  # Usar o backend correto
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from .forms import UploadFileForm
import pandas as pd
from io import BytesIO
import random
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from website.models import CustomUser
from django.http import HttpResponse
from django.core.mail import send_mail

User = get_user_model()

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


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Autenticar o usuário
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # Logar o usuário autenticado
            auth_login(request, user)
            return redirect('index')  # Redirecionar para a página inicial após o login
        else:
            return render(request, 'website/login.html', {'error': 'Credenciais inválidas'})
    return render(request, 'website/login.html')

def logout(request):
    # Usar a função logout do Django
    auth_logout(request)
    return redirect('index')  # Redirecionar para a página de login após o logout

def download_template(request):
    df_xlsx = write_standard_df()
    output = to_excel(df_xlsx)
    
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=template_padrao.xlsx'
    return response

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        # Não há necessidade de chamar writer.save()
    processed_data = output.getvalue()
    return processed_data

@login_required(login_url='login')
def predict(request):
    if request.method == 'POST':
        # Verifica se um arquivo foi enviado
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            try:
                # Processa o arquivo Excel
                df = pd.read_excel(uploaded_file)
                df_html = df.to_html()
            except Exception as e:
                return HttpResponse(f"Erro ao processar o arquivo: {str(e)}", status=400)
        else:
            df_html = None

        # Coleta outros dados do formulário
        forecast_name = request.POST.get('forecast_name', '')
        product_name = request.POST.get('product_name', '')
        model_options = request.POST.getlist('model_options')
        granularity = request.POST.get('granularity', '')
        test_percentage = request.POST.get('test_percentage', '')
        forecast_window = request.POST.get('forecast_window', '')

        # Aqui você pode adicionar lógica para processar os dados do formulário

        return render(request, 'website/predict.html', {
            'df_html': df_html,
            'forecast_name': forecast_name,
            'product_name': product_name,
            'model_options': model_options,
            'granularity': granularity,
            'test_percentage': test_percentage,
            'forecast_window': forecast_window,
        })

    return render(request, 'website/predict.html')
    # if request.method == 'POST':
    #     form = UploadFileForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         # Processar o arquivo aqui
    #         uploaded_file = request.FILES['file']
    #         if uploaded_file.name.endswith('.xlsx'):
    #             # Processar o arquivo de planilha
    #             pass
    #         else:
    #             # Mensagem de erro se o arquivo não for uma planilha
    #             return render(request, 'website/predict.html', {
    #                 'form': form,
    #                 'error': 'Por favor, faça upload de um arquivo Excel.'
    #             })
    # else:
    #     form = UploadFileForm()

    # # Gerar o template padrão para download
    # df_xlsx = write_standard_df()
    # df_xlsx = to_excel(df_xlsx)

    # return render(request, 'website/predict.html', {
    #     'form': form,
    #     'template_xlsx': df_xlsx
    # })

def write_standard_df():
    new_df = pd.DataFrame()
    new_df["Date"] = [datetime(year=2024, month=8, day=i) for i in range(1, 11)]
    new_df["Target"] = [100 * random.random() for _ in range(10)]
    return new_df

@login_required(login_url='login')
def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Verificar se o e-mail já está cadastrado
        if User.objects.filter(email=email).exists():
            return render(request, 'website/register.html', {'error': 'E-mail já cadastrado!'})

        # Criar o usuário
        user = User.objects.create_user(email=email, password=password)
        user.save()

        # Autenticar o usuário
        authenticated_user = authenticate(request, username=email, password=password)
        
        if authenticated_user is not None:
            # Logar o usuário autenticado
            auth_login(request, authenticated_user)
            return redirect('index')  # Redirecionar para a página inicial após o login
    return render(request, 'website/register.html')

def contact(request):
    success_message = None
    error_message = None

    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if not email and not phone:
            error_message = "Você precisa fornecer pelo menos um meio de contato: e-mail ou telefone."
        else:
            # Aqui você pode configurar o envio de um e-mail ou salvar os dados no banco de dados
            # Exemplo: send_mail(...)

            success_message = "Mensagem enviada com sucesso!"

    return render(request, 'website/contact.html', {
        'success_message': success_message,
        'error_message': error_message
    })