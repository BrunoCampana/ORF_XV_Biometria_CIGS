import mysql.connector

from biometria import *
from models import *
from mysql.connector import errorcode
from ctypes import create_string_buffer

#Arquivo global de configuração
config = {
  'user': 'root',
  'password': 'U3OkHxQ3M',
  'host': '127.0.0.1',
  'database': 'Biometria_CIGS',
}

#Buffer que armazena cada digital lida. Este construtor é necessário para suportar a função nativa em C
features_digital_1 = create_string_buffer(tamanho_buffer_digital)

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
    #iniciar_leitor()
    print ("Insira a digital do novo usuário:")
    ler_digital(features_digital_1)
    print ("Leitura realizada.")
    #finalizar_leitor()
    novo_usuario.biometria = features_digital_1
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
    #print(iniciar_leitor())
    print ("Insira a digital do usuário:")
    print (ler_digital(features_digital_1))
    print ("Leitura realizada.")
    #print(finalizar_leitor())

    cnx = get_new_connection()
    cursor = cnx.cursor()
    query_busca_usuarios = ("SELECT * FROM Usuario ")
    cursor.execute(query_busca_usuarios)

    usuario = Usuario()

    for (id,nome,Cod_PG,OM,Biometria) in cursor:
        #Código 1: digitais iguais
        if comparar_digitais(features_digital_1,Biometria) == 1:
            usuario.id = id
            usuario.nome = nome
            usuario.Cod_PG = Cod_PG
            usuario.OM = OM
            usuario.Biometria = Biometria

    cursor.close()
    cnx.close()

    return usuario

def registrar_entrada_saida():
    usuario = buscar_usuario_por_biometria()
    if not usuario.id:
        print ("Nenhum usuario encontrado")
        return None
    print ("Nome encontrado :" + usuario.nome)
