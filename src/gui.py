import tkinter as tk
import threading
import datetime
from tkinter import *
from tkinter import messagebox
from database_methods import *
from PIL import Image, ImageTk
import os
import csv


class minha_frame():
    def __init__():
        pass

class main_window(minha_frame):
        def __init__(self,master):
                self.master = master
                self.frame = tk.Frame(master)
                self.master.title("Controle de efetivo na Selva")
                self.app = None
                self.img_cigs = ImageTk.PhotoImage(Image.open("../img/cigs.png").resize((150,200), Image.ANTIALIAS))
                self.panel = Label(self.frame, image = self.img_cigs)
                self.panel.pack(pady = 30,anchor="c")
                self.lbl = Label(master , text = "Escolha sua opção:")
                self.lbl.place(relx=.5, rely=.41, anchor="c")

                self.botao_registrar_entrada_saida = Button(master ,
                                text = "Registrar entrada ou saída por biometria" ,
                                command = self.comando_registrar_entrada_saida,
                                height=3,
                                width=30 )
                self.botao_registrar_entrada_saida.place(relx=.5, rely=.5, anchor="c")

                self.botao_cadastrar_novo_usuario = Button(master ,
                                                            text="Cadastrar novo usuário",
                                                            command = self.comando_cadastrar_novo_usuario,
                                                            height=3,
                                                            width=30 )
                self.botao_cadastrar_novo_usuario.place(relx=.5, rely=.6, anchor="c")

                self.botao_liberar_entrada_saida_manualmente = Button(master ,
                                    text = "Liberar entrada ou saída manualmente" ,
                                    command = self.comando_liberar_entrada_saida_manualmente,
                                    height=3,
                                    width=30 )
                self.botao_liberar_entrada_saida_manualmente.place(relx=.5, rely=.7, anchor="c")

                self.botao_sair_do_sistema = Button(master ,
                                                    text = "Sair do sistema" ,
                                                    command = self.comando_sair_do_sistema,
                                                    height=3,
                                                    width=30 )
                self.botao_sair_do_sistema.place(relx=.5, rely=.8, anchor="c")

                self.frame.pack()

        def comando_registrar_entrada_saida(self):
                #Verifica se já há uma janela aberta, pois o leitor poderia já estar acionado
                if isinstance(self.app,minha_frame):
                    self.app.finalizar_janela()
                    if isinstance(self.app,ler_digital_window):
                        cancelar_leitura()
                        self.thread_leitura.join()
                self.newWindow = tk.Toplevel(self.frame)
                self.app = ler_digital_window(self.newWindow)
                self.thread_leitura = threading.Thread(target=registrar_entrada_saida,
                                                    kwargs={'callback': self.app.retorno_busca_biometrica})
                self.thread_leitura.start()

        def comando_cadastrar_novo_usuario(self):
                if isinstance(self.app,minha_frame):
                    self.app.finalizar_janela()
                    if isinstance(self.app,ler_digital_window):
                        cancelar_leitura()
                        self.thread_leitura.join()
                self.newWindow = tk.Toplevel(self.frame)
                self.app = cadastrar_novo_usuario_window(self.newWindow,self.callback_cadastro_novo_usuario)

        def comando_liberar_entrada_saida_manualmente(self):
                if isinstance(self.app,minha_frame):
                    self.app.finalizar_janela()
                    if isinstance(self.app,ler_digital_window):
                        cancelar_leitura()
                        self.thread_leitura.join()
                self.newWindow = tk.Toplevel(self.master)
                self.app = autenticacao_operador_window(self.newWindow,self.callback_liberacao_usuario_manual)

        def comando_sair_do_sistema(self):
                if isinstance(self.app,ler_digital_window):
                    cancelar_leitura()
                    self.thread_leitura.join()
                    finalizar_leitor()
                self.master.destroy()

        #Os callbacks são chamados para dar continuidade nas tabelas
        #Assim que uma tela termina seu fluxo, chama o seu callback para continuar para a outra tela
        def callback_cadastro_novo_usuario(self,usuario):
                self.newWindow = tk.Toplevel(self.master)
                self.app = ler_digital_window(self.newWindow)
                self.thread_leitura = threading.Thread(target=cadastro_novo_usuario,kwargs={'novo_usuario': usuario,
                                                                                    'callback':self.app.finalizar_janela})
                self.thread_leitura.start()

        def callback_liberacao_usuario_manual(self):
                self.newWindow = tk.Toplevel(self.master)
                self.app = selecionar_usuario_window(self.newWindow)

class ler_digital_window(minha_frame):
        def __init__(self , master):
                self.master = master
                self.master.geometry("240x120")
                self.master.title("Leitura Biométrica")
                self.lbl = Label(master , text = "Insira a impressão digital:",pady=10)
                self.lbl.pack()
                self.master.protocol("WM_DELETE_WINDOW",self.finalizar_janela)
                self.quitButton = tk.Button(self.master, text = 'Cancelar', width = 25 , command = self.finalizar_janela)
                self.quitButton.pack(anchor="s",pady=10)
                self.isDead = False


        def finalizar_janela(self):
            cancelar_leitura()
            self.isDead = True
            self.master.destroy()

        def not_found(self):
                messagebox.showinfo("Aviso", "Usuário não encontrado", icon="warning")

        #Método que funciona como uma forma de CALLBACK da thread que realiza a leitura da impressão digital
        def retorno_busca_biometrica(self,usuario,evento):
            if self.isDead == True:
                return
            elif usuario.id == 0:
                self.not_found()
                self.finalizar_janela()
            elif usuario.id == -1:
                self.finalizar_janela()
            else:
                self.newWindow = tk.Toplevel(self.master)
                self.app = selecionar_missao_window(self.newWindow,usuario,evento,self.finalizar_janela)

class selecionar_missao_window(minha_frame):
    def __init__(self,master,usuario,evento,callback):
        self.callback = callback
        self.usuario = usuario
        self.evento = evento
        self.master = master
        self.frame = tk.Frame(master)
        self.master.title("Cadastro de Evento")

        # Converter do formato do MySQL para o formato brasileiro
        data_obj = datetime.datetime.strptime(evento.data, "%Y-%m-%d %H:%M:%S")
        string_label = id_posto_graduacao_dict[usuario.Cod_PG] + " " + usuario.nome + \
                        "\nEvento: " + tipo_evento_dict[evento.id_tipo] + \
                        "\nHorário: " + data_obj.strftime('%d-%m-%Y %H:%M:%S')

        self.lbl = Label(master , text=string_label)
        self.lbl.pack()

        self.variable = tk.StringVar(master)
        # Como opção DEFAULT, o primeiro campo do dicionário
        default_str = list(missoes_dict.keys())[0]
        self.variable.set(default_str)
        self.opt = default_str
        self.missaoOPT = tk.OptionMenu(master, self.variable, *missoes_dict,command=self.mudanca_opcao_selecao)
        self.missaoOPT.pack()
        self.OBSlbl = Label(master, text="Observações:")
        self.OBS = Entry(master)
        self.OBSlbl.pack()
        self.OBS.pack()

        self.registrar_evento_button = tk.Button(self.frame, text = 'Registrar', width = 25 , command = self.comando_registrar_evento)
        self.registrar_evento_button.pack()
        self.frame.pack()

    def mudanca_opcao_selecao(self,value):
        self.opt = value

    def comando_registrar_evento(self):
        self.evento.observacoes = self.OBS.get()
        self.evento.id_missao = missoes_dict[self.opt]
        registrar_evento_no_banco_de_dados(self.evento)
        messagebox.showinfo("Sucesso", "Evento cadastrado no banco de dados", icon="info")

        self.finalizar_janela()

    def finalizar_janela(self):
        self.master.destroy()
        self.callback()

class cadastrar_novo_usuario_window(minha_frame):
        def __init__(self , master,callback):
                self.master = master
                self.master.title("Cadastro de novo usuario")
                self.master.geometry("300x240")
                self.usernamelbl = Label(master, text="Nome:")
                self.username = Entry(master)
                self.variable = tk.StringVar(master)
                # Como opção DEFAULT, o primeiro campo do dicionário
                default_str = list(posto_graduacao_dict.keys())[0]
                self.variable.set(default_str)
                self.opt = default_str
                self.PGlbl = Label(self.master, text="Posto/Graduação:")

                self.PGopt = tk.OptionMenu(self.master, self.variable, *posto_graduacao_dict,command=self.mudanca_opcao_selecao)
                self.OMlbl = Label(self.master, text="OM:")
                self.OM = Entry(master)
                self.cadastrar_button = tk.Button(self.master, text = 'Cadastrar', width = 25 , command = self.ler_digital_novo_usuario)
                self.cancel_button = tk.Button(self.master, text='Cancelar', width = 25, command= self.finalizar_janela)

                self.callback = callback

                self.usernamelbl.pack(pady=4)
                self.username.pack()
                self.OMlbl.pack(pady=4)
                self.OM.pack()
                self.PGlbl.pack(pady=4)
                self.PGopt.pack()

                self.cadastrar_button.pack(pady=4)
                self.cancel_button.pack(pady=4)


        def mudanca_opcao_selecao(self,value):
            self.opt = value

        def ler_digital_novo_usuario(self):
            usuario = Usuario()
            usuario.nome = self.username.get()
            usuario.OM = self.OM.get()
            usuario.Cod_PG = posto_graduacao_dict[self.opt]

            self.callback(usuario)
            self.master.destroy()

        def finalizar_janela(self):
            self.master.destroy()

class selecionar_usuario_window(minha_frame):

        def __init__(self , master):
                self.dicionario_usuarios = retornar_lista_usuarios()
                self.master = master
                if len(self.dicionario_usuarios) == 0:
                    messagebox.showinfo("Aviso","Nenhum usuario encontrado",icon="warning")
                    self.master.destroy()
                else:
                    self.frame = tk.Frame(master)
                    master.title("Registrar Evento Manualmente")
                    self.lbl = Label(master , text = "Escolher Militar:")
                    self.lbl.pack()
                    self.variable1 = tk.StringVar(master)
                    self.variable2 = tk.StringVar(master)

                    # Como opção DEFAULT, o primeiro campo do dicionário
                    default_str1 = list(self.dicionario_usuarios.keys())[0]
                    self.variable1.set(default_str1)
                    self.opt1 = default_str1
                    self.milOpt = tk.OptionMenu(master, self.variable1, *self.dicionario_usuarios,command=self.mudanca_opcao_selecao1)
                    self.milOpt.pack()

                    default_str2 = list(missoes_dict.keys())[0]
                    self.variable2.set(default_str2)
                    self.opt2 = default_str2
                    self.misOpt = tk.OptionMenu(master, self.variable2, *missoes_dict,command=self.mudanca_opcao_selecao2)
                    self.misOpt.pack()

                    self.OBSlbl = Label(master, text="Observações:")
                    self.OBS = Entry(master)
                    self.OBSlbl.pack()
                    self.OBS.pack()
                    self.registrar_button = tk.Button(self.frame, text='Registrar', width = 25, command= self.comando_registrar_evento)
                    self.cancel_button = tk.Button(self.frame, text = 'Cancelar', width = 25 , command = self.finalizar_janela)
                    self.registrar_button.pack()
                    self.cancel_button.pack()
                    self.frame.pack()

        def mudanca_opcao_selecao1(self,value):
            self.opt1 = value
        def mudanca_opcao_selecao2(self,value):
            self.opt2 = value

        def comando_registrar_evento(self):
                usuario_id = self.dicionario_usuarios[self.opt1]
                ultimo_evento_id = buscar_ultimo_tipo_evento_usuario(usuario_id)
                evento = criar_novo_evento(ultimo_evento_id,usuario_id)
                evento.id_missao = missoes_dict[self.opt2]
                evento.observacoes = self.OBS.get()
                registrar_evento_no_banco_de_dados(evento)
                # Converter do formato do MySQL para o formato brasileiro
                data_obj = datetime.datetime.strptime(evento.data, "%Y-%m-%d %H:%M:%S")
                string_label = "Evento Cadastrado:\n" + self.opt1 + \
                            "\nEvento: " + tipo_evento_dict[evento.id_tipo] + \
                            "\nHorário: " + data_obj.strftime('%d-%m-%Y %H:%M:%S')
                messagebox.showinfo("Sucesso", string_label, icon="info")

                self.finalizar_janela()

        def finalizar_janela(self):
                self.master.destroy()

class autenticacao_operador_window(minha_frame):

        def __init__(self , master,callback):
                self.master = master
                self.frame = tk.Frame(master)
                master.title("Login de operador")
                self.callback = callback
                self.username_text = Label(master, text="Usuário:")
                self.username_guess = Entry(master)
                self.password_text = Label(master, text="Senha:")
                self.password_guess = Entry(master, show="*")
                self.attempt_login_button = tk.Button(self.frame, text='Login', width = 25, command= self.try_login)
                self.cancel_button = tk.Button(self.frame, text = 'Cancelar', width = 25 , command = self.finalizar_janela)
                self.username_text.pack()
                self.username_guess.pack()
                self.password_text.pack()
                self.password_guess.pack()
                self.attempt_login_button.pack()
                self.cancel_button.pack()
                self.frame.pack()

        def try_login(self):
            if autenticar_operador(self.username_guess.get(),self.password_guess.get()):
                self.master.destroy()
                self.callback()
            else:
                messagebox.showinfo("Aviso", "Falha na autenticação", icon="warning")

        def finalizar_janela(self):
                self.master.destroy()
