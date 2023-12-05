import os
from dotenv import load_dotenv
# Carga las variables de entorno desde el archivo .env
load_dotenv()

from azure.communication.email import EmailClient

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/send_email', methods=['POST'])
def send_email():
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
    try:
        connection_string = os.environ.get("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients":  {
                "to": [{"address": data['email']}],
            },
            "content": {
                "subject": data['subject'],
                "plainText": data['body'],
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