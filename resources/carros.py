from flask import Blueprint, jsonify, request
from banco import db
from models.modelCarro import Carro
from flask_jwt_extended import jwt_required
import locale
import smtplib

carros = Blueprint('carros', __name__)


@carros.route('/carros', methods=['POST'])
def inclusao():
    carro = Carro.from_json(request.json)
    db.session.add(carro)
    db.session.commit()
    return jsonify(carro.to_json()), 201


@carros.route('/carros')
def listagem():
    carros = Carro.query.order_by(Carro.modelo).all()
    return jsonify([carro.to_json() for carro in carros])


@carros.route('/carros/<int:id>')
def consulta(id):
    # obtém o registro a ser alterado (ou gera um erro 404 - not found)
    carro = Carro.query.get_or_404(id)
    return jsonify(carro.to_json()), 200


@carros.route('/carros/alterar/<int:id>', methods=['PUT'])
def alteracao(id):
    # obtém o registro a ser alterado (ou gera um erro 404 - not found)
    carro = Carro.query.get_or_404(id)

    # recupera os dados enviados na requisição
    carro.modelo = request.json['modelo']
    carro.cor = request.json['cor']
    carro.ano = request.json['ano']
    carro.preco = request.json['preco']
    carro.destaque = request.json['destaque']
    carro.foto = request.json['foto']
    carro.quant = request.json['quant']

    # altera (pois o id já existe)
    db.session.add(carro)
    db.session.commit()
    return jsonify(carro.to_json()), 204


@carros.errorhandler(404)
def id_invalido(error):
    return jsonify({'id': 0, 'message': 'not found'}), 404


# -----------------------------------------------------------------------------------------------------------!


@carros.route('/carros/destaque')
def destaque():
    # obtém registro dos carros que estão em destaque
    carros = Carro.query.order_by(Carro.destaque).filter(
        Carro.destaque.like(f'%{"x"}%')).all()
    # converte cada carro para o formato json
    return jsonify([carro.to_json() for carro in carros])


@carros.route('/carros/destacar/<int:id>', methods=['PUT'])
def destacar(id):
    # obtém o registro a ser alterado ou gera um error 404 - not found
    carro = Carro.query.get_or_404(id)

    if carro.destaque == 'x':
        carro.destaque = ' '
    else:
        carro.destaque = 'x'

    db.session.add(carro)
    db.session.commit()
    return 'Tudo certo :)'


@carros.route('/carros/filtro/<palavra>')
def pesquisa(palavra):
    # obtém todos os registros da tabela carros em ordem de modelo
    carros = Carro.query.order_by(Carro.modelo).filter(
        Carro.modelo.like(f'%{palavra}%')).all()
    # converte a lista de carros para o formato JSON
    return jsonify([carro.to_json() for carro in carros])


@carros.route('/enviaemail')
def enviaemail():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('luizyoutube96@hotmail.com', '******')
    server.set_debuglevel(1)
    server.sendmail('luizyoutube96@hotmail.com',
                    'luizyoutube96@hotmail.com',
                    'Subject: "\nProposta Recebida!\n')
    server.quit()
    return jsonify({"Message": "E-mail enviado!"})


@carros.route('/carros/dadosestatisticos')
def dadosestatisticos():
    if db.session.query(Carro).count() == 0:
        quant = 0
        media = 0
        total = 0
    else:
        # formatação de moeda
        locale.setlocale(locale.LC_ALL, '')

        quant = db.session.query(db.func.count(Carro.id)).first()[0]

        db_media = db.session.query(db.func.avg(Carro.preco)).first()[0]
        media = locale.currency(db_media, grouping=True, symbol=None)

        db_total = db.session.query(db.func.sum(
            Carro.quant*Carro.preco)).first()[0]
        total = locale.currency(db_total, grouping=True, symbol=None)

        # retorna em json os dados estatísticos dos carros
        return jsonify([quant, media, total])
