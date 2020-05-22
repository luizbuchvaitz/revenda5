from flask import Flask, jsonify
from config import config
from banco import db
from resources.carros import carros
from resources.marcas import marcas
from resources.usuarios import usuarios
from flask_jwt_extended import JWTManager
from blacklist import blacklist
import smtplib
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
jwt = JWTManager(app)
#LIBERA TODAS AS ROTAS (NÃO É A MELHOR, OPÇÃO)
#A MELHOR FORMA, É A VISTA NO EXEMPLO ANTERIOR, INDICAR QUAIS ROTAS DEVE SER LIBERADAS PARA ACESSO CORS
CORS(app)

app.register_blueprint(carros)
app.register_blueprint(marcas)
app.register_blueprint(usuarios)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@app.route('/')
def raiz():
    return '<h2>Revenda Herbie</h2>'


@app.route('/enviaemail')
def envia():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('luizyoutube96@gmail.com', '*********')
    server.set_debuglevel(1)
    server.sendmail('luizyoutube96@gmail.com', 
                    'luizyoutube96@gmail.com', 
                    'Subject: Aula de PI2\nOlá... testando mensagem\nNova linha')
    server.quit()
    return jsonify({"Message": "E-mail enviado..."})


@app.route('/criadb')
def criadb():
    db.create_all()
    return "Ok! Tabelas criadas com sucesso"


if __name__ == '__main__':
    app.run(debug=True)
