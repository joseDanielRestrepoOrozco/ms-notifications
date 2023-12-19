import os
import random
from dotenv import load_dotenv
from bson import DBRef, ObjectId
# Carga las variables de entorno desde el archivo .env
load_dotenv()

from azure.communication.email import EmailClient

from flask import Flask, request, jsonify

from flask_cors import CORS

from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

def get_database():
 
   CONNECTION_STRING = "mongodb+srv://root:root@urbannavsecurity.dceqvez.mongodb.net/?retryWrites=true&w=majority"
 
   client = MongoClient(CONNECTION_STRING)
 
   return client['security']

@app.route('/send_email', methods=['POST'])
def send_email():
    
    html_file_path = "plantillas/Correo_codigo.html"
    html_content = ''

    # Lee el contenido del archivo HTML
    with open(html_file_path, 'r', encoding= 'utf8') as file:
        html_content = file.read()

    # Obtener datos del cuerpo de la solicitud
    data = request.json

    # Verificar si se proporcionaron todos los campos necesarios
    if 'email' not in data or 'subject' not in data or 'body' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Simular el envío de un correo electrónico (aquí puedes agregar tu lógica real de envío de correo electrónico)
    # En este ejemplo, simplemente imprimimos la información recibida en la consola.
    print(f"Email: {data['email']}")
    print(f"Asunto: {data['subject']}")
    print(f"Cuerpo: {data['body']}")
    html_content_number = html_content.replace("$$$", data['body'])
    try:
        connection_string =os.environ.get("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)
        print(connection_string)
        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients":  {
                "to": [{"address": data['email']}],
            },
            "content": {
                "subject": data['subject'],
                "html": html_content_number
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        print(ex)
    return jsonify({'message': 'Email sent successfully'}), 200

@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.json

    random_digits = ''.join(random.choices('123456789', k=4))

    databaseConnection = get_database()
    collection_session = databaseConnection['session']
    collection_users = databaseConnection['user'] 

    user_document=collection_users.find_one({"_id": ObjectId(data["_id"])})
    findEmail = collection_session.find_one({"user": DBRef('user', user_document["_id"])})

    if findEmail:
        collection_session.update_one(
        {"user": DBRef('user', user_document["_id"])},
        {"$set": {"code": random_digits}}
    )
    else:

        newData = {
            "user": DBRef('user', user_document["_id"]),
            "active": False,
            "code": random_digits,
            "_class": "com.msurbaNavSecurity.msurbaNavSecurity.Models.Session"
        }

        collection_session.insert_one(newData)


    html_file_path = "plantillas/change_password.html"
    html_content = ''

    # Lee el contenido del archivo HTML
    with open(html_file_path, 'r', encoding= 'utf8') as file:
        html_content = file.read()

    print(f"Email: {data['email']}")

    # Genera los 4 dígitos aleatorios para el "body"
    html_content_number = html_content.replace("$$$", random_digits)

    try:
        connection_string =os.environ.get("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)
        print(connection_string)
        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients":  {
                "to": [{"address": data['email']}],
            },
            "content": {
                "subject": "Código para cambiar contraseña UrbanNav",
                "html": html_content_number
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        print(ex)
    return jsonify({'message': 'Email sent successfully'}), 200


if __name__ == '__main__':
    # Utiliza Waitress como servidor en lugar del servidor de desarrollo de Flask para producción
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)