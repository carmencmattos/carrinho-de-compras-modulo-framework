from fastapi import FastAPI
from typing import List
from typing import Union
from typing import TypedDict
from pydantic import BaseModel

app = FastAPI()
OK = "OK"
FALHA = "FALHA"


# Classe representando os dados do endereço do cliente.
class Endereco(BaseModel):
    id: Union[int, None] = None
    id_usuario: int
    rua: str
    cep: str
    cidade: str
    estado: str
    
    
# Classe representando os dados do cliente.
class Usuario(BaseModel):
    id: int
    nome: str
    email: str


# Classe representando os dados do produto.
class Produto(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float


# Classe representando o carrinho de compras de um cliente com uma lista de produtos.
class CarrinhoDeCompras():
    id_usuario: int
    produtos: List[Produto] = []
    preco_total: float
    quantidade_de_produtos: int


# Databases.
db_usuarios = {}
db_produtos = {}
db_end = {}        
db_carrinhos = {}


# Cadastrar um usuário com um nome e um e-mail. 
# Um usuário irá ter um código identificador único no sistema.
@app.post("/usuario/")
async def criar_usuario(usuario: Usuario):
    if usuario.id in db_usuarios:
        return "Id já existente"
    db_usuarios[usuario.id] = usuario
    return OK


# Consultar um usuário pelo seu código identificador.
@app.get("/usuario/{id}")
async def retornar_usuario_pelo_id(id: int):
    if id in db_usuarios:
        return db_usuarios[id]
    return FALHA


# Consultar um usuário pelo primeiro nome dele.
@app.get("/usuario/")
async def retornar_usuario_pelo_nome(nome: str):
    for id in db_usuarios:
        if db_usuarios[id].nome == nome:
            return db_usuarios[id]
    return FALHA


# Remover um usuário pelo código dele.
@app.delete("/usuario/{id}")
async def deletar_usuario(id: int):
    if id in db_usuarios:
        db_usuarios.pop(id)
        return OK
    return FALHA


# Pesquisar pelos endereços de um usuário.
@app.get("/usuario/{id_usuario}/enderecos/")
async def retornar_enderecos_do_usuario(id_usuario: int):
    enderecos = []
    if id_usuario not in db_usuarios:
        return FALHA
    for id in db_end:
        if db_end[id].id_usuario == id_usuario:
            enderecos.append(db_end[id])
    return enderecos


# Retornar emails dos usuários.
@app.get("/usuarios/emails/")
async def retornar_emails(dominio: str):
    return FALHA


# Cadastrar o(s) endereço(s) do usuário.
@app.post("/endereco/")
async def criar_endereco(endereco: Endereco):
    if endereco.id_usuario not in db_usuarios:
        return FALHA
    if endereco.id in db_end:
        return "Id já existente"
    id_novo_endereco = len(list(db_end)) + 1
    endereco.id = id_novo_endereco
    db_end[id_novo_endereco] = endereco
    return OK


# Remover um endereço do usuário pelo seu código identificador.
@app.delete("/endereco/{id_endereco}")
async def deletar_endereco(id_endereco: int):
    if id_usuario in db_usuarios:
        return id_usuario[id_usuario].enderecos.pop(id_endereco)
    return FALHA


# Cadastrar um produto, que possua nome, descrição, preço e código identificador.
@app.post("/produto/")
async def criar_produto(produto: Produto):
    if produto.id in db_produtos:
        return "Id já existente"
    db_produtos[produto.id] = produto
    return OK


# Retornar os produtos existentes no db_produtos.
@app.get("/produto/")
async def retornar_produtos():
    return db_produtos


# Remover um produto pelo código.
@app.delete("/produto/{id_produto}/")
async def deletar_produto(id_produto: int):
    if id_produto in db_produtos:
        db_produtos.pop(id_produto)
        return OK
    return FALHA

# Criar um carrinho de compras associado a um usuário.
# Adicionar produtos ao carrinho de compras.
# Calcular o valor total do carrinho.
@app.post("/carrinho/{id_usuario}/{id_produto}/")
async def adicionar_carrinho(id_usuario: int, id_produto: int):
    if id_usuario not in db_usuarios or id_produto not in db_produtos:
        return FALHA

    if id_usuario in db_carrinhos:
        db_carrinhos[id_usuario].produtos.append(db_produtos[id_produto])
        db_carrinhos[id_usuario].preco_total = db_carrinhos[id_usuario].preco_total + \
            db_produtos[id_produto].preco
        db_carrinhos[id_usuario].quantidade_de_produtos = len(
            db_carrinhos[id_usuario].produtos)
    else:
        carrinho_de_compras = CarrinhoDeCompras()
        carrinho_de_compras.id_usuario = id_usuario
        carrinho_de_compras.produtos.append(db_produtos[id_produto])

        carrinho_de_compras.preco_total = 0.0
        carrinho_de_compras.preco_total = carrinho_de_compras.preco_total + \
            db_produtos[id_produto].preco

        carrinho_de_compras.quantidade_de_produtos = len(
            carrinho_de_compras.produtos)

        db_carrinhos[id_usuario] = carrinho_de_compras

    return OK


# Retornar o carrinho de compras.
@app.get("/carrinho/{id_usuario}/")
async def retornar_carrinho(id_usuario: int):
    if id_usuario not in db_carrinhos:
        return FALHA
    carrinho_de_compras = CarrinhoDeCompras()
    carrinho_de_compras.id_usuario = db_carrinhos[id_usuario].id_usuario
    carrinho_de_compras.produtos = db_carrinhos[id_usuario].produtos
    carrinho_de_compras.preco_total = db_carrinhos[id_usuario].preco_total
    carrinho_de_compras.quantidade_de_produtos = db_carrinhos[id_usuario].quantidade_de_produtos
    return carrinho_de_compras


# Remover produtos do carrinho de compras.
@app.delete("/carrinho/{id_usuario}/produto/{id_produto}/")
async def remover_produto(id_usuario: int, id_produto: int):
    if id_usuario not in db_carrinhos:
        return FALHA
    if id_produto not in db_produtos:
        return FALHA

    db_carrinhos[id_usuario].produtos.remove(db_produtos[id_produto])
    db_carrinhos[id_usuario].preco_total = 0
    for produto in db_carrinhos[id_usuario].produtos:
        db_carrinhos[id_usuario].preco_total = db_carrinhos[id_usuario].preco_total + \
            produto.preco
        db_carrinhos[id_usuario].quantidade_de_produtos = len(
            db_carrinhos[id_usuario].produtos)
    return OK


# Retornar o número de itens e o valor total do carrinho de compras.
@app.get("/carrinho/{id_usuario}/total")
async def retornar_total_carrinho(id_usuario: int):
    if id_usuario not in db_carrinhos:
        return FALHA
    numero_itens = 0
    valor_total = 0.0
    for produto in db_carrinhos[id_usuario].produtos:
        numero_itens = numero_itens + 1
        valor_total = valor_total + produto.preco
    return numero_itens, valor_total


# Deletar o carrinho correspondente ao id_usuario e retornar OK
@app.delete("/carrinho/{id_usuario}/")
async def deletar_carrinho(id_usuario: int):
    if id_usuario in db_carrinhos:
        db_carrinhos.pop(id_usuario)
        return OK
    return FALHA


# Saudação de boas-vindas.
@app.get("/")
async def bem_vinda():
    site = "Seja bem-vinda"
    return site.replace('\n', '')
