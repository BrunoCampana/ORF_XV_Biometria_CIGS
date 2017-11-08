import mysql.connector
import datetime

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

#Buffer que armazena cada digital lida. Este construtor é necessário para suportar a função nativa em C
digital_features = create_string_buffer(tamanho_buffer_digital)

# Dicionários globais mapeando IDs para strings
#P/G
posto_graduacao_dict = {}
#Tipos
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

def cadastrar_novo_usuario():
    novo_usuario = formulario_usuario()
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
            "(id_usuario, id_tipo, data) "
            "VALUES (%s, %s, %s)")
    #O valor que deve ser salvo para a biometria do usuário é acessado através do atributo RAW (binário)
    parametros_query = (evento.id_usuario,evento.id_tipo,evento.data)
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

def registrar_entrada_saida():
    usuario = buscar_usuario_por_biometria()
    if not usuario.id:
        print ("Nenhum usuario encontrado")
        return None
    print ("Nome encontrado : " + usuario.nome)
    ultimo_tipo_evento = buscar_ultimo_tipo_evento_usuario(usuario.id)
    #Se o último evento foi uma entrada, registrar saída da selva
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
    evento = Evento()
    evento.id_usuario = usuario.id
    evento.id_tipo = tipo
    evento.data = data_atual.strftime('%Y-%m-%d %H:%M:%S')
    registrar_evento_no_banco_de_dados(evento)

#Métodos que são chamados na inicialização do sistema para obter os postos e graduações
def obter_postos_graduacoes_e_criar_dicionario():
    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_busca_pgs = ("SELECT * FROM Posto_Graduacao")
    cursor.execute(query_busca_pgs)
    for (id,PG) in cursor:
        posto_graduacao_dict[id] = PG
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
