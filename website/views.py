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
from datetime import timezone
import firebase_admin
from firebase_admin import credentials, initialize_app

FIREBASE_SERVICE_ACCOUNT_KEY = './supplyprophet-firebase-adminsdk-kmfel-9ffc14f771.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://supplyprophet-default-rtdb.firebaseio.com/',
        'storageBucket': 'supplyprophet.appspot.com'
    })

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

        # Coleta outros dados do formulário
        forecast_name = request.POST.get('forecast_name', '')
        product_name = request.POST.get('product_name', '')
        model_options = request.POST.getlist('model_options')
        granularity = request.POST.get('granularity', '')
        test_percentage = request.POST.get('test_percentage', '')
        forecast_window = request.POST.get('forecast_window', '')

        # Verifica se um arquivo foi enviado
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            try:             
                # Processa o arquivo Excel
                df = pd.read_excel(uploaded_file)

                df_media = df["quantidade vendas"].rolling(5).mean()

                datas_setembro = pd.date_range(start='2024-09-01', end='2024-09-30', freq='D')
                df_setembro = pd.DataFrame(datas_setembro, columns=['Data'])

                df_marge = pd.concat([df_setembro, df_media], axis=1)
                df_marge['Data'] = df_marge['Data'].dt.date

                plt.figure(figsize=(10, 6))
                plt.plot(df_marge['Data'], df_marge['quantidade vendas'], marker='o')
                plt.title(f"Gráfico previsões vendas de {product_name}")
                plt.xlabel('data')
                plt.ylabel('demanda')

                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()
                graphic = base64.b64encode(image_png).decode('utf-8')

                df_html = df_marge.T.to_html()
            except Exception as e:
                return HttpResponse(f"Erro ao processar o arquivo: {str(e)}", status=400)
        else:
            df_html = None



        # Aqui você pode adicionar lógica para processar os dados do formulário

        return render(request, 'website/predict.html', {
            'graphic': graphic,
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

class MockPrediction:
    def __init__(self, forecast_name, product_name, model_options, granularity, test_percentage, forecast_window, created_at):
        self.forecast_name = forecast_name
        self.product_name = product_name
        self.model_options = model_options
        self.granularity = granularity
        self.test_percentage = test_percentage
        self.forecast_window = forecast_window
        self.created_at = created_at

def mock_predictions():
    models = ['ARIMA', 'SARIMA', 'ARMAX', 'PROPHET']
    granularities = ['DIA', 'HORA', 'MINUTO']
    windows = ['1 mês', '6 meses', '1 ano']
    predictions = []

    for i in range(10):  # Mocking 10 predictions
        predictions.append({
            'id': i,
            'forecast_name': f'Previsão {i+1}',
            'product_name': f'Produto {random.choice(["A", "B", "C"])}',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'model': random.choice(models),
            'graph_url': 'https://via.placeholder.com/600x400.png?text=Gr%C3%A1fico+de+Previs%C3%A3o',
            'details': 'Detalhes sobre a previsão.',
            'granularity': random.choice(granularities),
            'test_percentage': random.randint(60, 80),
            'forecast_window': random.choice(windows)
        })

    return predictions

def prediction_list(request):
    # Mocked data for demonstration
    predictions = [
        {
            'id': 1,
            'forecast_name': 'Forecast 1',
            'product_name': 'Product A',
            'date': '2024-09-18',
            'details': 'Details about this prediction',
            'granularity': 'Monthly',
            'test_percentage': 20,
            'forecast_window': 6,
            'models': ['SARIMA', 'ARIMA', 'Prophet']  # List of models
        },
        {
            'id': 2,
            'forecast_name': 'Forecast 2',
            'product_name': 'Product B',
            'date': '2024-09-19',
            'details': 'Details about this prediction',
            'granularity': 'Weekly',
            'test_percentage': 15,
            'forecast_window': 3,
            'models': ['SARIMA', 'Prophet']  # List of models
        },
        # Add more mocked predictions as needed
    ]

    context = {
        'predictions': predictions
    }

    return render(request, 'website/prediction_list.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from firebase_admin import storage
from firebase_admin import db

# Salvar dados no Realtime Database
def save_data_to_realtime_db(data, path):
    ref = db.reference(path)
    ref.set(data)

# Ler dados do Realtime Database
def get_data_from_realtime_db(path):
    ref = db.reference(path)
    return ref.get()

# Fazer upload de um arquivo
def upload_file_to_storage(file, bucket_name, storage_path):
    bucket = storage.bucket(name=bucket_name)
    blob = bucket.blob(storage_path)
    blob.upload_from_file(file)
    return blob.public_url

# Fazer download de um arquivo
def download_file_from_storage(storage_path, local_file_path, bucket_name):
    bucket = storage.bucket(name=bucket_name)
    blob = bucket.blob(storage_path)
    blob.download_to_filename(local_file_path)

@csrf_exempt
def save_data_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        path = data.get('path')
        content = data.get('content')
        save_data_to_realtime_db(content, path)
        return JsonResponse({'status': 'success'})

@csrf_exempt
def get_data_view(request):
    if request.method == 'GET':
        path = request.GET.get('path')
        data = get_data_from_realtime_db(path)
        return JsonResponse({'data': data})
import io
@csrf_exempt
def upload_file_view(request):
    if request.method == 'POST' and request.FILES:
        file = request.FILES['file']
        bucket_name = 'your-firebase-bucket'
        storage_path = 'uploads/' + file.name
        
        # Convert the file to a BytesIO object
        file_io = io.BytesIO(file.read())
        
        # Upload to Firebase Storage
        public_url = upload_file_to_storage(file_io, bucket_name, storage_path)
        
        return JsonResponse({'status': 'success', 'url': public_url})
    return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)

@csrf_exempt
def download_file_view(request):
    if request.method == 'GET':
        file_name = request.GET.get('file_name')
        local_path = '/tmp/' + file_name
        bucket_name = 'your-firebase-bucket'
        storage_path = 'uploads/' + file_name
        download_file_from_storage(storage_path, local_path, bucket_name)
        with open(local_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
