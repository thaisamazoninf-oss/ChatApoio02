from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO
import json
import os
import csv
import sys
from datetime import datetime
import webbrowser
import threading
from werkzeug.utils import secure_filename

# FUNÇÃO PARA OBTER CAMINHO DO ARQUIVO, FUNCIONA TANTO EM DESENVOLVIMENTO QUANTO EM EXECUTÁVEL  
def caminho_arquivo(nome):

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, nome)
    
    return os.path.join(os.path.abspath("."), nome)


app = Flask(
    __name__,
    template_folder=caminho_arquivo("templates"),
    static_folder=caminho_arquivo("static")
)

socketio = SocketIO(
    app,
    async_mode="threading"
)

print("Modo SocketIO:", socketio.async_mode)

app.secret_key = "senha_super_secreta"


ARQUIVO_JSON = caminho_arquivo("chamados.json")
ARQUIVO_APOIO = caminho_arquivo("apoio_chat.json")
ARQUIVO_APOIOS = caminho_arquivo("apoios.json")
ARQUIVO_AGENDA = caminho_arquivo("agenda.csv")


# CRIAR JSON CASO NÃO EXISTA
if not os.path.exists(ARQUIVO_JSON):

    with open(ARQUIVO_JSON, "w") as f:
        json.dump([], f)

if not os.path.exists(ARQUIVO_APOIO):

    with open(ARQUIVO_APOIO, "w") as f:
        json.dump({}, f)




# LER CHAMADOS
def ler_chamados():

    try:

        with open(
            ARQUIVO_JSON,
            "r",
            encoding="utf-8"
        ) as f:

            conteudo = f.read().strip()

            if not conteudo:
                return []

            return json.loads(conteudo)

    except:
        return []


# SALVAR CHAMADOS
def salvar_chamados(chamados):

    with open(
        ARQUIVO_JSON,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            chamados,
            f,
            indent=4,
            ensure_ascii=False
        )

# LER APOIO CHAT
def ler_lista_apoios():
    try:

        with open(
            ARQUIVO_APOIOS,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as erro:
        print(erro)

        return []
    
def ler_apoio():

    try:

        with open(
            ARQUIVO_APOIO,
            "r",
            encoding="utf-8"
        ) as f:

            conteudo = f.read().strip()

            if not conteudo:
                return {}

            return json.loads(conteudo)

    except:

        return {}

# SALVAR APOIO CHAT
def salvar_apoio(dados):

    with open(
        ARQUIVO_APOIO,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            dados,
            f,
            indent=4,
            ensure_ascii=False
        )

# CARREGAR linhas CSV        
def carregar_linhas():
    linhas = []
    
    with open(
        ARQUIVO_AGENDA,
        "r",
        encoding="utf-8-sig"
    )as arquivo:
        
        leitor = csv.DictReader(arquivo)
        
        for linha in leitor:
            print(linha)
            break  # Remover ou comentar este break para ler todas as linhas

    return linhas

# OBTER ANALISTA ATUAL
def obter_atendimento_atual():
    
    agora = datetime.now()
    
    dias = {
        0:"Segunda",
        1:"Terça",
        2:"Quarta",
        3:"Quinta",
        4:"Sexta",
        5:"Sábado",
        6:"Domingo"
    }
    
    dia_atual = dias.get(agora.weekday())

    if not dia_atual:
        return None, None
    
    hora_atual = agora.strftime("%H:%M")
    
    atual = None
    proximo = None

    with open(
        ARQUIVO_AGENDA,
        "r",
        encoding="utf-8"
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        print("COLUNAS:")
        print(leitor.fieldnames)  # Exibir os nomes das colunas para verificação

        linhas = list(leitor)
    
        for i, linha in enumerate(linhas):
            horario = linha["Horario"]
            inicio, fim = horario.split("-")

            if inicio <= hora_atual < fim:
                atual = {
                    "analista": linha[dia_atual],
                    "horario_inicio": inicio,
                    "horario_fim": fim
                }

                if i + 1 < len(linhas):
                    prox = linhas[i + 1]
                    prox_inicio, prox_fim = (
                        prox["Horario"].split("-")
                    )

                    proximo = {
                        "analista": prox[dia_atual],
                        "horario_inicio": prox_inicio,
                        "horario_fim": prox_fim
                    }
                
                break     

    return atual, proximo

# PÁGINA PRINCIPAL
@app.route("/")
def index():

    chamados = ler_chamados()

    ordem_status = {
        "Aguardando": 0,
        "Assumiu atendimento": 1,
        "Tentando contato com usuário": 2,
        "Em ligação": 3,
        "Não atendeu": 4
    }

    chamados.sort(
        key=lambda x: ordem_status.get(x["status"], 99)
    )

    atual, proximo = obter_atendimento_atual()

    lista_apoios = ler_lista_apoios()

    apoio = ler_apoio()
    
    return render_template(
        "index.html",
        chamados=chamados,
        atual=atual,
        proximo=proximo,
        apoio_status=apoio.get("status"),
        apoio_nome=apoio.get("nome"),
        apoios=lista_apoios,
        admin=session.get("admin")
    )

# LOGIN ADMIN
@app.route(
        "/login-admin",
        methods=["POST"]
)

# ROTA PARA LOGIN DE ADMINISTRADOR, VERIFICA SE A SENHA ESTÁ CORRETA E DEFINE SESSÃO DE ADMINISTRADOR
def login_admin():

    senha = request.form.get("senha")

    if senha == "admin123":

        session["admin"] = True

        return jsonify({"success": True})
    
    return jsonify({"success": False})

# LOGOUT ADMIN
@app.route("/logout-admin")
def logout_admin():

    session.pop("admin", None)

    return jsonify({"success": True})

#UPLOAD ADMIN
@app.route("/upload-arquivos", 
            methods=["POST"]
)

# ROTA PARA UPLOAD DE IMAGEM E CSV, APENAS PARA ADMINISTRADOR
def upload_arquivos():

    if not session.get("admin"):
        return jsonify({
            "success": False
        })

# OBTER ARQUIVOS ENVIADOS
    imagem = request.files.get("imagem")
    csv_file = request.files.get("csv")

    if imagem:
        
        extensão = os.path.splitext(
            imagem.filename
        )[1].lower()

        imagem.save( 
            os.path.join(
                caminho_arquivo("static"),
                f"calendar{extensão}"
            )
        )

    socketio.emit("atualizar")

# SALVAR CSV ENVIADO, SUBSTITUINDO O EXISTENTE
    if csv_file:
        csv_file.save(
            ARQUIVO_AGENDA
        )
    
    socketio.emit("atualizar")
    return jsonify({
        "success": True
    })

# CRIAR CHAMADO
@app.route("/criar", methods=["POST"])
def criar_chamado():

    chamados = ler_chamados()

    numero = request.form.get("chamado")

    novo = {
        "id": len(chamados) + 1,
        "chamado": numero,
        "status": "Aguardando",
        "tecnico": ""
    }

    chamados.append(novo)

    salvar_chamados(chamados)

    socketio.emit("atualizar")

    return jsonify({"success": True})


# ASSUMIR ATENDIMENTO
@app.route("/assumir/<int:id>", methods=["POST"])
def assumir(id):

    chamados = ler_chamados()

    dados = request.get_json()

    tecnico = dados.get("tecnico")

    for chamado in chamados:

        if chamado["id"] == id:

            chamado["status"] = "Assumiu atendimento"

            chamado["tecnico"] = tecnico

    salvar_chamados(chamados)

    socketio.emit("atualizar")

    return jsonify({"success": True})


# INICIAR LIGAÇÃO
@app.route("/contato/<int:id>", methods=["POST"])
def contato(id):

    chamados = ler_chamados()

    for chamado in chamados:

        if chamado["id"] == id:

            chamado["status"] = "Tentando contato com usuário"

    salvar_chamados(chamados)

    socketio.emit("atualizar")

    return jsonify({"success": True})


# CONTATO REALIZADO
@app.route("/contato-realizado/<int:id>", methods=["POST"])
def contato_realizado(id):

    chamados = ler_chamados()

    for chamado in chamados:

        if chamado["id"] == id:

            chamado["status"] = "Em ligação"

    salvar_chamados(chamados)

    socketio.emit("atualizar")

    return jsonify({"success": True})


# NÃO ATENDEU
@app.route("/nao-atendeu/<int:id>", methods=["POST"])
def nao_atendeu(id):

    chamados = ler_chamados()

    for chamado in chamados:

        if chamado["id"] == id:

            chamado["status"] = "Não atendeu"

    salvar_chamados(chamados)

    socketio.emit("atualizar")

    return jsonify({"success": True})


# CONCLUIR CHAMADO
@app.route("/concluir/<int:id>", methods=["POST"])
def concluir(id):

    chamados = ler_chamados()

    chamados = [
        chamado for chamado in chamados
        if chamado["id"] != id
    ]

    salvar_chamados(chamados)

    socketio.emit("atualizar")

    return jsonify({"success": True})

# SOLICITAR APOIO NO CHAT
@app.route("/solicitar-apoio", methods=["POST"])
def solicitar_apoio():

    salvar_apoio({
        "status": "solicitado",
    })

    socketio.emit("atualizar")

    return jsonify({"success": True})

# DEFINIR APOIO
@app.route("/definir-apoio", methods=["POST"])
def definir_apoio():

    dados = request.get_json()

    nome = dados.get("nome")

    salvar_apoio({
        "status": "em_apoio",
        "nome": nome
    })

    socketio.emit("atualizar")

    return jsonify({"success": True})

# ENCERRAR APOIO
@app.route("/encerrar-apoio", methods=["POST"])
def encerrar_apoio():

    salvar_apoio({})

    socketio.emit("atualizar")

    return jsonify({"success": True})


@app.route("/dados-painel")
def dados_painel():

    chamados = ler_chamados()

    atual, proximo = obter_atendimento_atual()

    apoio = ler_apoio()

    return jsonify({
        "atual": atual,
        "proximo": proximo,
        "apoio_status": apoio.get("status"),
        "apoio_nome": apoio.get("nome"),
        "chamados": chamados,
    })


def abrir_navegador():

    webbrowser.open(
        "http://localhost:5000"
    )


# EXECUTAR SERVIDOR
if __name__ == "__main__":

    threading.Timer(
        1,
        abrir_navegador
    ).start()

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )