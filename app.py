from flask import Flask, render_template, request
import qrcode
from io import BytesIO
from PIL import Image
import requests
import base64

app = Flask(__name__)

# Page d'accueil qui affiche le formulaire
@app.route('/')
def index():
    return render_template('index.html', qr_code=None)

# Génération du QR Code et affichage
@app.route('/', methods=['POST'])
def generate_qr_code():
    data = request.form['data']
    color = request.form['color']
    background_color = request.form['background_color']
    logo_url = request.form['logo_url']

    # Générer le QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=color, back_color=background_color).convert("RGBA")

    # Ajouter le logo si une URL est fournie
    if logo_url:
        try:
            response = requests.get(logo_url)
            if response.status_code == 200:
                logo = Image.open(BytesIO(response.content)).convert("RGBA")
                logo_size = (qr_img.size[0] // 4, qr_img.size[1] // 4)
                logo = logo.resize(logo_size)
                qr_img.paste(logo, ((qr_img.size[0] - logo_size[0]) // 2, (qr_img.size[1] - logo_size[1]) // 2), logo)
        except Exception as e:
            print(f"Erreur lors de l'ajout du logo : {e}")

    # Sauvegarder le QR Code dans un fichier temporaire
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    # Encoder en base64
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('index.html', qr_code=qr_code_base64)

if __name__ == '__main__':
    app.run(debug=True)
