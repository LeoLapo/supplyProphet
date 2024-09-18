import firebase_admin
from firebase_admin import credentials, db, storage

# Caminho para o arquivo JSON de configuração do Firebase
cred = credentials.Certificate('./supplyprophet-firebase-adminsdk-kmfel-9ffc14f771.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://supplyprophet-default-rtdb.firebaseio.com/',
    'storageBucket': 'supplyprophet.appspot.com'  # Confirme se o bucket está correto
})