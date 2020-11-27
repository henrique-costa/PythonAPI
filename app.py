"""
Trabalho de Desenvolvimento de Software para WEB 2
prof. Cris

Alunos: Henrique, Alexander, Matheus Missaci
"""
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from sqlalchemy.orm import relationship
from marshmallow_sqlalchemy import ModelSchema
import enum
import datetime as dt

"""
Configuracoes do Banco e Flask:
Login: root
Senha: jscslfh
Porta: 3306
Db: testdb
"""
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:jscslfh@:3306/testdb' 
db = SQLAlchemy(app) # Adiciona o banco com suporte SQLAlchemy ao app


"""
---------------------------------------- MODELS ------------------------------------------------------------//
"""
# MODEL CLIENTE ------------<
class Cliente(db.Model):
    __tableName__ = "cliente"
    cliente_id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    telefone = db.Column(db.String(15))
    email = db.Column(db.String(90))
    numero = db.Column(db.String(90))
    orcamentos = db.relationship("Orcamento", back_populates="cliente")
    endereco_id = db.Column(db.Integer, db.ForeignKey('endereco.endereco_id'))
    endereco = db.relationship("Endereco", back_populates="clientes", uselist=False)
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    def _init_(self, nome, telefone, email, numero, endereco_id):
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.numero = numero
        self.endereco_id = endereco_id
    def __repr__(self):
        return '' % self.cliente_id

# MODEL ENDERECO ------------<
class Endereco(db.Model):
    __tableName__ = "endereco"
    endereco_id = db.Column(db.Integer, primary_key=True)
    cep = db.Column(db.String(11))
    logradouro = db.Column(db.String(70))
    cidade = db.Column(db.String(90))
    estado = db.Column(db.String(2))
    clientes = db.relationship("Cliente", back_populates="endereco")
    def _init_(self, cep, logradouro, cidade, estado):
        self.cep = cep
        self.logradouro = logradouro
        self.cidade = cidade
        self.estado = estado
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self    
    def __repr__(self):
        return '' % self.endereco_id 

# MODEL ORCAMENTO ------------<
class Orcamento(db.Model):
    __tableName__ = "orcamento"
    orcamento_id = db.Column(db.Integer, primary_key=True)
    createDate = db.Column(db.Date)
    total = db.Column(db.Float)
    status = db.Column(db.Integer)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.cliente_id'))
    cliente = db.relationship("Cliente", back_populates="orcamentos", uselist=False)
    detalhesOrcamento = db.relationship("DetalheOrcamento", back_populates="orcamento")
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    def _init_(self, createDate, total, status):
        self.createDate = createDate
        self.total = total
        self.status = status
    def __repr__(self):
        return '' % self.orcamento_id

# MODEL ORCAMENTO ------------<
class DetalheOrcamento(db.Model):
    __tableName__ = "detalheOrcamento"
    detalheOrcamento_id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer)
    custoTotal = db.Column(db.Float)
    produto_id = db.Column(db.Integer)
    nomeDoProduto = db.Column(db.String(100))
    preco = db.Column(db.Float)
    orcamento_id = db.Column(db.Integer, db.ForeignKey('orcamento.orcamento_id'))
    orcamento = db.relationship("Orcamento", back_populates="detalhesOrcamento", uselist=False)
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    def _init_(self, quantidade, custoTotal, produto_id, nomeDoProduto, preco):
        self.quantidade = quantidade
        self.custoTotal = custoTotal
        self.produto_id = produto_id
        self.nomeDoProduto = nomeDoProduto
        self.preco = preco
    def __repr__(self):
        return '' % self.detalheOrcamento_id

class OrcamentoStatus(enum.Enum):
    CRIADA = 0
    CONFIRMADA = 1
    CANCELADA = 2
       
db.create_all()  

"""
---------------------------------------- DB SCHEMAS ------------------------------------------------------------//
"""
# Detalhe Orcamento ------------<
class DetalheOrcamentoMapping(ModelSchema):
    class Meta:
        model = DetalheOrcamento #Especifica o modelo referencia do Schema
        sqla_session = db.session #abre sessao com banco
    #propiredades da Classe/Model:
    detalheOrcamento_id = fields.Integer(dump_only=True)
    quantidade = fields.Number(required=True)
    custoTotal = fields.Number(required=True)
    produto_id = fields.Integer(required=True)
    nomeDoProduto = fields.String(required=True)
    preco = fields.Number(required=True)

# Orcamento ------------<
class OrcamentoMapping(ModelSchema):
    class Meta:
        model = Orcamento
        sqla_session = db.session
    orcamento_id = fields.Integer(dump_only=True)
    createDate = fields.Date(required=True)
    total = fields.Number(required=True)
    status = fields.Number(required=True)
    detalhesOrcamento = fields.List(fields.Nested(DetalheOrcamento))

# Cliente ------------<
class ClienteMapping(ModelSchema):
    class Meta:
        model = Cliente
        sqla_session = db.session
    cliente_id = fields.Integer(dump_only=True)
    nome = fields.String(required=True)
    telefone = fields.String(required=True)
    email = fields.String(required=True)
    numero = fields.String(required=True)
    endereco_id = fields.Integer(dump_only=True)
    orcamentos = fields.List(fields.Nested(OrcamentoMapping))

# Endereco ------------<
class EnderecoMapping(ModelSchema):
    class Meta:
        model = Endereco
        sqla_session = db.session
    endereco_id = fields.Integer(dump_only=True)
    cep = fields.String(required=True)
    logradouro = fields.String(required=True)
    cidade = fields.String(required=True)
    estado = fields.String(required=True)
    clientes = fields.List(fields.Nested(ClienteMapping))


# metodos da API:    
"""
---------------------------------------- CLIENTE ------------------------------------------------------------//
"""
@app.route('/ListCliente', methods = ['GET']) #config da rota
def getClientes(): #declaracao do metodo
    listAll = Cliente.query.all() #query all lcientes
    cliente_schema = ClienteMapping(many=True) #definir schema e relationship
    clientes = cliente_schema.dump(listAll) #dump model
    return make_response(jsonify({"clientes": clientes})) #retorna resposta em json

@app.route('/CreateCliente', methods = ['POST'])
def postCliente():
    data = request.get_json()
    cliente_schema = ClienteMapping()
    cliente = cliente_schema.load(data)
    result = cliente_schema.dump(cliente.create())
    return make_response(jsonify({"cliente": result}),200)   
    

"""
---------------------------------------- ENDERECO ------------------------------------------------------------//
"""
@app.route('/ListEndereco', methods = ['GET'])
def getEnderecos():
    listAll = Endereco.query.all()
    endereco_schema = EnderecoMapping(many=True)
    enderecos = endereco_schema.dump(listAll)
    return make_response(jsonify({"enderecos": enderecos}))

@app.route('/CreateEndereco', methods = ['POST'])
def postEndereco():
    data = request.get_json()
    endereco_schema = EnderecoMapping()
    endereco = endereco_schema.load(data)
    result = endereco_schema.dump(endereco.create())
    return make_response(jsonify({"endereco": result}),200)


"""
---------------------------------------- ORCAMENTO ------------------------------------------------------------//
"""
@app.route('/ListOrcamento', methods = ['GET'])
def getOrcamento():
    listAll = Orcamento.query.all()
    orcamento_schema = OrcamentoMapping(many=True)
    orcamentos = orcamento_schema.dump(listAll)
    return make_response(jsonify({"orcamentos": orcamentos}))
    
@app.route('/CreateOrcamento', methods = ['POST'])
def postOrcamento():
    data = request.get_json()
    orcamento_schema = OrcamentoMapping()
    orcamento = orcamento_schema.load(data)
    result = orcamento_schema.dump(orcamento.create())
    return make_response(jsonify({"orcamento": result}),200)
     
@app.route('/EditOrcamento/<id>', methods = ['PUT'])
def putOrcamento(id):
    data = request.get_json()
    get_orcamento = Orcamento.query.get(id)
    if data.get('createDate'):
        get_orcamento.createDate = data['createDate']
    if data.get('total'):
        get_orcamento.total = data['total']
    if data.get('status'):
        get_orcamento.status = data['status']
    db.session.add(get_orcamento)
    db.session.commit()
    orcamento_schema = OrcamentoMapping(only=['orcamento_id', 'createDate', 'total','status'])
    orcamento = orcamento_schema.dump(get_orcamento)
    return make_response(jsonify({"orcamento": orcamento}))

"""
---------------------------------------- DETALHE ORCAMENTO ------------------------------------------------------------//
"""
@app.route('/EditDetalheOrcamento/<id>', methods = ['PUT'])
def putDetalheOrcamento(id):
    data = request.get_json()
    detalheOrcamento = DetalheOrcamento.query.get(id)
    if data.get('quantidade'):
        detalheOrcamento.quantidade = data['quantidade']
    if data.get('custoTotal'):
        detalheOrcamento.custoTotal = data['custoTotal']
    if data.get('produto_id'):
        detalheOrcamento.produto_id = data['produto_id']
    if data.get('nomeDoProduto'):
        detalheOrcamento.nomeDoProduto = data['nomeDoProduto']
    if data.get('preco'):
        detalheOrcamento.preco = data['preco']
    db.session.add(detalheOrcamento)
    db.session.commit()
    detalhe_orcamento_schema = DetalheOrcamentoMapping(only=['detalheOrcamento_id', 'quantidade', 'custoTotal','produto_id', 'nomeDoProduto', 'preco'])
    detalhe_orcamento = detalhe_orcamento_schema.dump(detalheOrcamento)
    return make_response(jsonify({"detalhe_orcamento": detalhe_orcamento}))
    
@app.route('/DeleteDetalheOrcamento/<id>', methods = ['DELETE'])
def deleteOrcamentoDetalheById(id):
    getById = DetalheOrcamento.query.get(id)
    if getById:
        db.session.delete(getById)
        db.session.commit()
        return make_response(jsonify({"status": "success"}),200)
    return make_response("",204)