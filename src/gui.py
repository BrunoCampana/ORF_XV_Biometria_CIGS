import tkinter as tk
import threading
import datetime
from tkinter import *
from tkinter import messagebox
from database_methods import *

class main_window():
        def __init__(self,master):
                self.master = master
                self.frame = tk.Frame(master)
                self.master.title("Controle de efetivo na Selva")
                self.app = None
                self.lbl = Label(master , text = "Escolha sua opção:")
                self.lbl.pack()

                self.botao_registrar_entrada_saida = Button(master ,
                                text = "Registrar entrada ou saída por biometria" ,
                                command = self.comando_registrar_entrada_saida )
                self.botao_registrar_entrada_saida.pack()

                self.btn2 = Button(master , text = "Cadastrar novo usuário" , command = self.command2 )
                self.btn2.pack()

                self.btn3 = Button(master , text = "Liberar entrada ou saída manualmente" , command = self.command3 )
                self.btn3.pack()

                self.btn4 = Button(master , text = "Sair do sistema" , command = self.command4 )
                self.btn4.pack()

                self.frame.pack()

        def comando_registrar_entrada_saida(self):
                #Verifica se já há uma janela aberta
                if isinstance(self.app,ler_digital_window):
                    self.app.finalizar_janela()
                    self.thread_leitura.join()
                self.newWindow = tk.Toplevel(self.master)
                self.app = ler_digital_window(self.newWindow)
                self.thread_leitura = threading.Thread(target=registrar_entrada_saida,
                                                    kwargs={'callback': self.app.retorno_busca_biometrica})
                self.thread_leitura.start()

        def command2(self):
                self.newWindow = tk.Toplevel(self.master)
                self.app = windowclass2(self.newWindow)

        def command3(self):
                self.newWindow = tk.Toplevel(self.master)
                self.app = windowclass3(self.newWindow)

        def command4(self):
                self.master.destroy()

class ler_digital_window():
        def __init__(self , master):
                self.master = master
                self.frame = tk.Frame(master)
                self.master.title("Leitura de Impressão digital")
                self.lbl = Label(master , text = "Insira a impressão digital:")
                self.lbl.pack()
                self.master.protocol("WM_DELETE_WINDOW",self.finalizar_janela)
                self.quitButton = tk.Button(self.frame, text = 'Cancelar', width = 25 , command = self.finalizar_janela)
                self.quitButton.pack()
                self.isDead = False
                self.frame.pack()


        def finalizar_janela(self):
            cancelar_leitura()
            self.isDead = True
            self.master.destroy()

        def not_found(self):
                messagebox.showinfo("Aviso", "Usuário não encontrado", icon="warning")


        def retorno_busca_biometrica(self,usuario,evento):
            if self.isDead == True:
                return
            elif usuario.id == 0:
                self.not_found()
                self.finalizar_janela()
            else:
                self.newWindow = tk.Toplevel(self.master)
                self.app = selecionar_missao_window(self.newWindow,usuario,evento,self.finalizar_janela)

class selecionar_missao_window():
    def __init__(self,master,usuario,evento,callback):
        self.callback = callback
        self.usuario = usuario
        self.evento = evento
        self.master = master
        self.frame = tk.Frame(master)
        self.master.title("Cadastro de Evento")
        # Converter do formato do MySQL para o formato brasileiro
        data_obj = datetime.datetime.strptime(evento.data, "%Y-%m-%d %H:%M:%S")
        string_label = "Nome: " + usuario.nome + \
                        "\nEvento: " + tipo_evento_dict[evento.id_tipo] + \
                        "\nHorário: " + data_obj.strftime('%d-%m-%Y %H:%M:%S')

        self.lbl = Label(master , text=string_label)
        self.lbl.pack()

        self.variable = tk.StringVar(master)
        # Como opção DEFAULT, o primeiro campo do dicionário
        default_str = list(missoes_dict.keys())[0]
        self.variable.set(default_str)
        self.opt = default_str
        self.missaoOPT = tk.OptionMenu(master, self.variable, *missoes_dict,command=self.func)
        self.missaoOPT.pack()
        self.OBSlbl = Label(master, text="Observações:")
        self.OBS = Entry(master)
        self.OBSlbl.pack()
        self.OBS.pack()

        self.registrar_evento_button = tk.Button(self.frame, text = 'Registrar', width = 25 , command = self.comando_registrar_evento)
        self.registrar_evento_button.pack()
        self.frame.pack()

    def func(self,value):
        self.opt = value

    def comando_registrar_evento(self):
        self.evento.observacoes = self.OBS.get()
        self.evento.id_missao = missoes_dict[self.opt]
        registrar_evento_no_banco_de_dados(self.evento)
        self.finalizar_janela()

    def finalizar_janela(self):
        self.master.destroy()
        self.callback()

class windowclass1():
        def __init__(self , master):
                self.username = ("goi") #Pegar do BD
                self.password = ("123")
                self.master = master
                self.frame = tk.Frame(master)
                self.master.title("Login")
                self.username_text = Label(master, text="Usuário:")
                self.username_guess = Entry(master)
                self.password_text = Label(master, text="Senha:")
                self.password_guess = Entry(master, show="*")
                self.quitButton = tk.Button(self.frame, text = 'Cancelar', width = 25 , command = self.close_window)
                self.attempt_login = tk.Button(self.frame, text='Login', width = 25, command= self.try_login)
                self.username_text.pack()
                self.username_guess.pack()
                self.password_text.pack()
                self.password_guess.pack()
                self.quitButton.pack()
                self.attempt_login.pack()
                self.frame.pack()

        def try_login(self):
            #self.username = ("goi")
            #self.password = ("123")
                if self.username_guess.get() == self.username:
                    self.newWindow = tk.Toplevel(self.master)
                    self.app = windowclass4(self.newWindow)
                else:
                    messagebox.showinfo("Erro", "Não Reconhecido", icon="warning")

        def close_window(self):
                self.master.destroy()

class MenuOpcoes(tk.OptionMenu):
        def __init__(self, master, status, *options):
                self.var = StringVar(master)
                self.var.set(status)
                OptionMenu.__init__(self, master, self.var, *options)

class windowclass2():
        def __init__(self , master):
                self.master = master
                self.frame = tk.Frame(master)
                master.title("Cadastro")
                # Cria o label e a caixa de texto para o Nome
                self.username_text = Label(master, text="Nome:")
                self.username_guess = Entry(master)
                self.posto = Label(master, text="Posto:")
                self.mymenu1 = MyOptionMenu(self.frame, 'Select status', 'General','Coronel','Tenente-Coronel', 'Major', 'Capitão', '1º Tenente', '2º Tenente', 'Cadete', 'Sargento', 'Soldado')
                self.password_text = Label(master, text="OM:")
                self.password_guess = Entry(master)
                self.quitButton = tk.Button(self.frame, text = 'Cancelar', width = 25 , command = self.close_window)
                self.attempt_login = tk.Button(self.frame, text='Cadastrar', width = 25, command= self.try_login)
                self.username_text.pack()
                self.username_guess.pack()

                self.mymenu1.pack()
                self.password_text.pack()
                self.password_guess.pack()
                self.posto.pack()
                self.quitButton.pack()
                self.attempt_login.pack()
                self.frame.pack()

       # def MyOptionMenu(OptionMenu):
        #        self.var = StringVar(master)
         #       self.var.set(status)
          #      OptionMenu.__init__(self, master, self.var, *options)

        def try_login(self):
                self.newWindow = tk.Toplevel(self.master)
                self.app = windowclass3(self.newWindow)


        def close_window(self):
                self.master.destroy()


class windowclass4():
        def __init__(self , master):
                self.master = master
                self.frame = tk.Frame(master)
                master.title("Cadastre Evento")
                self.lbl = Label(master , text = "Escolher Militar:")
                self.mymenu1 = MyOptionMenu(self.frame, 'Select status', 'mickey', 'donald', 'luizinho', 'jorginho')
                self.lbl.pack()

                self.mymenu1.pack()

                self.quitButton = tk.Button(self.frame, text = 'Cancelar', width = 25 , command = self.close_window)
                self.attempt_login = tk.Button(self.frame, text='Cadastrar Evento do Militar', width = 25, command= self.try_login)
                self.quitButton.pack()
                self.attempt_login.pack()
                self.frame.pack()

        def try_login(self):
                messagebox.showinfo("Sucesso", "Evento Cadastrado", icon="info")

        def close_window(self):
                self.master.destroy()


class windowclass5():
        def __init__(self , master):
                self.master = master
                self.frame = tk.Frame(master)
                master.title("Buscar")
                self.username_text = Label(master, text="Buscar:")
                self.username_text.pack()
                self.mymenu1 = MyOptionMenu(self.frame, 'Select status', 'mickey', 'donald', 'luizinho', 'jorginho')
                self.mymenu1.pack()
                self.frame.pack()


def main_loop():
    obter_postos_graduacoes_e_criar_dicionario()
    obter_tipos_eventos_e_criar_dicionario()
    obter_tipos_missoes_e_criar_dicionario()
    iniciar_leitor()
    root = Tk()
    root.title("Principal")
    root.geometry("400x300")
    cls = main_window(root)
    root.mainloop()
    cancelar_leitura()
    finalizar_leitor()
