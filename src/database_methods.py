import mysql.connector
import datetime
import getpass
import hashlib

from biometria import *
from models import *
from mysql.connector import errorcode
from ctypes import create_string_buffer

#Arquivo global de configuração
config = {
  'user': 'matissek',
  'password': '1234',
  'host': '192.168.23.1',
  'database': 'Biometria_CIGS',
}

#UTILIDADES

#Buffer que armazena cada digital lida. Este construtor é necessário para suportar a função nativa em C
digital_features = create_string_buffer(tamanho_buffer_digital)
# Dicionários globais mapeando strings para IDs
#P/G e Missões
posto_graduacao_dict = {}
missoes_dict = {}
# Dicionários globais mapeando IDs para strings
#P/G e Tipos de eventos
id_posto_graduacao_dict = {}
tipo_evento_dict = {}

def get_new_connection():
    try:
      cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("[!] Acesso negado.")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("[!] Banco de dados inexistente.")
      else:
        print("[!] Um erro ocorreu ao conectar ao banco de dados.")
    return cnx;

def cadastro_novo_usuario(novo_usuario,callback=None):
    print ("Insira a digital do novo usuário:")
    if (ler_digital(digital_features) != 1):
        print ("Cadastro cancelado")
        return
    print ("Leitura realizada.")
    novo_usuario.biometria = digital_features
    cadastrar_novo_usuario(novo_usuario)
    if callback is not None:
        callback()

##Função usada somente pela GUI
def formulario_usuario():
    novo_usuario = Usuario()
    novo_usuario.nome = input("Nome: ")
    novo_usuario.Cod_PG = input("Código do Posto/Graduação: ")
    novo_usuario.OM = input("OM: ")
    print ("Insira a digital do novo usuário:")
    ler_digital(digital_features)
    print ("Leitura realizada.")
    novo_usuario.biometria = digital_features
    return novo_usuario

def cadastrar_novo_usuario(novo_usuario):
#    novo_usuario = formulario_usuario()
    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_cadastro_usuario = ("INSERT INTO Usuario "
            "(nome, Cod_PG, OM, Biometria) "
            "VALUES (%s, %s, %s, %s)")
    #O valor que deve ser salvo para a biometria do usuário é acessado através do atributo RAW (binário)
    parametros_query = (novo_usuario.nome,novo_usuario.Cod_PG,
                        novo_usuario.OM,novo_usuario.biometria.raw)
    cursor.execute(query_cadastro_usuario, parametros_query)
    print ("Cadastro realizado com sucesso.")
    cnx.commit()
    cursor.close()
    cnx.close()


def buscar_usuario_por_biometria():
    print ("Insira a digital do usuário:")
    ler_digital(digital_features)
    print ("Leitura realizada.")

    cnx = get_new_connection()
    cursor = cnx.cursor()
    #Ignorar usuarios sem biometria
    query_busca_usuarios = ("SELECT * FROM Usuario WHERE Biometria is NOT NULL ")
    cursor.execute(query_busca_usuarios)

    usuario = Usuario()

    for (id,nome,Cod_PG,OM,Biometria) in cursor:
        #Código 1: digitais iguais
        if comparar_digitais(digital_features,Biometria) == 1:
            usuario.id = id
            usuario.nome = nome
            usuario.Cod_PG = Cod_PG
            usuario.OM = OM
            usuario.Biometria = Biometria

    cursor.close()
    cnx.close()

    return usuario

def registrar_evento_no_banco_de_dados(evento):
    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_cadastro_evento = ("INSERT INTO Evento "
            "(id_usuario, id_tipo, cod_missao, data, obs) "
            "VALUES (%s, %s, %s, %s, %s)")
    #O valor que deve ser salvo para a biometria do usuário é acessado através do atributo RAW (binário)
    parametros_query = (evento.id_usuario,evento.id_tipo,evento.id_missao, evento.data,evento.observacoes)
    cursor.execute(query_cadastro_evento, parametros_query)
    cnx.commit()
    cursor.close()
    cnx.close()

# Método para buscar o último evento (ENTRADA ou SAÍDA) do usuário
def buscar_ultimo_tipo_evento_usuario(id_usuario):
    cnx = get_new_connection()
    cursor = cnx.cursor()
    # A busca selecionará o último evento registrado
    query_busca_tipo_evento = ("SELECT id_tipo FROM Evento "
                            "WHERE id_usuario = %s ORDER BY id DESC LIMIT 1")
    parametros_query = (id_usuario,)
    cursor.execute(query_busca_tipo_evento,parametros_query)

    # Se não houver último evento, obrigatoriamente ele estará entrando na SELVA,
    # logo consideraremos que o último evento foi um retorno da SELVA
    row = cursor.fetchone()
    if row is None:
        ultimo_tipo_evento = 2
    else:
        ultimo_tipo_evento = row[0]
    return ultimo_tipo_evento

def criar_novo_evento(ultimo_tipo_evento,usuario_id):
    if ultimo_tipo_evento == 1:
        tipo = 2
        print ("Evento: " + tipo_evento_dict[tipo])
    #Se o último evento foi uma saída, registrar entrada na selva
    elif ultimo_tipo_evento == 2:
        tipo = 1
        print ("Evento: " + tipo_evento_dict[tipo])
    else:
        #Outros tipos podem ser inseridos aqui além de entrada/saída (trabalho futuro)
        pass

    data_atual = datetime.datetime.now()
    print ("Data e horário: " + data_atual.strftime('%d-%m-%Y %H:%M:%S'))
    evento = Evento()
    evento.id_usuario = usuario_id
    evento.id_tipo = tipo
    evento.data = data_atual.strftime('%Y-%m-%d %H:%M:%S')
    return evento

def registrar_entrada_saida(callback=None):
    usuario = buscar_usuario_por_biometria()
    #ID 0 : nenhum usuario encontrado
    if not usuario.id:
        print ("Nenhum usuario encontrado")
        evento = None
    else:
        print ("Nome encontrado : " + usuario.nome)
        ultimo_tipo_evento = buscar_ultimo_tipo_evento_usuario(usuario.id)
        #Se o último evento foi uma entrada, registrar saída da selva
        evento = criar_novo_evento(ultimo_tipo_evento,usuario.id)
        #registrar_evento_no_banco_de_dados(evento)
    if callback is not None:
        callback(usuario,evento)
    return usuario

#Métodos que são chamados na inicialização do sistema para obter os postos e graduações
def obter_postos_graduacoes_e_criar_dicionario():
    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_busca_pgs = ("SELECT * FROM Posto_Graduacao")
    cursor.execute(query_busca_pgs)
    for (id,PG) in cursor:
        id_posto_graduacao_dict[id] = PG
        posto_graduacao_dict[PG] = id
    cursor.close()
    cnx.close()

def obter_tipos_eventos_e_criar_dicionario():
    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_busca_tipos = ("SELECT * FROM Tipo")
    cursor.execute(query_busca_tipos)
    for (id,tipo) in cursor:
        tipo_evento_dict[id] = tipo
    cursor.close()
    cnx.close()

def obter_tipos_missoes_e_criar_dicionario():
    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_busca_missoes = ("SELECT id_missao,nome FROM missao")
    cursor.execute(query_busca_missoes)
    for (id,nome) in cursor:
        missoes_dict[nome] = id
    cursor.close()
    cnx.close()

def buscar_usuario_manualmente():
    query = '%' + str.upper(input("Nome parcial do usuário:")) + '%'

    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_busca_operador = ("SELECT id,nome,Cod_PG FROM Usuario "
                        "WHERE UPPER(nome) LIKE %s ")
    parametros_query = (query,)
    cursor.execute(query_busca_operador,parametros_query)
    print ("Usuários encontrados")
    for (id,nome,Cod_PG) in cursor:
        print (str(id) + " - " + nome)
    escolha = input("ID do usuario para liberar:")
    ultimo_tipo_evento = buscar_ultimo_tipo_evento_usuario(escolha)
    evento = criar_novo_evento(ultimo_tipo_evento,escolha)
    registrar_evento_no_banco_de_dados(evento)

#Para liberar manualmente, é necessário autenticar o operador
def autenticar_operador(login,senha):
    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_busca_operador = ("SELECT * FROM admins "
                "WHERE usuario = %s AND senha = %s LIMIT 1")
    hash_senha = hashlib.sha256(senha.encode('utf-8')).hexdigest()
    parametros_query = (login ,hash_senha)
    cursor.execute(query_busca_operador,parametros_query)

    #Retorna verdadeiro se pelo menos um resultado for encontrado
    row = cursor.fetchone()
    if row is None:
        return False
    else:
        return True

def liberar_entrada_saida_manualmente():
    print ("[!] É necessária a autorização para acesso a esta funcionalidade")
    login = input("Login:")
    senha = getpass.getpass("Senha:")
    if (autenticar_operador(login,senha) is False):
        print ("[!] Operador não encontrado.")
        return None
    print ("Autenticação de operador bem-sucedida.")
    buscar_usuario_manualmente()

def retornar_lista_usuarios():
    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_busca_usuarios = ("SELECT id,Cod_PG,nome FROM Usuario ")
    cursor.execute(query_busca_usuarios)
    dict_users = {}
    for (id,Cod_PG,nome) in cursor:
        dict_users[id_posto_graduacao_dict[Cod_PG] + " " + nome] = id
    return dict_users
