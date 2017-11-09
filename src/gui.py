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

                self.botao_cadastrar_novo_usuario = Button(master ,
                                                            text="Cadastrar novo usuário",
                                                            command = self.comando_cadastrar_novo_usuario )
                self.botao_cadastrar_novo_usuario.pack()

                self.botao_liberar_entrada_saida_manualmente = Button(master ,
                                    text = "Liberar entrada ou saída manualmente" ,
                                    command = self.comando_liberar_entrada_saida_manualmente )
                self.botao_liberar_entrada_saida_manualmente.pack()

                self.botao_sair_do_sistema = Button(master ,
                                                    text = "Sair do sistema" ,
                                                    command = self.comando_sair_do_sistema )
                self.botao_sair_do_sistema.pack()

                self.frame.pack()

        def comando_registrar_entrada_saida(self):
                #Verifica se já há uma janela aberta, pois o leitor poderia já estar acionado
                if isinstance(self.app,ler_digital_window):
                    self.app.finalizar_janela()
                    self.thread_leitura.join()
                self.newWindow = tk.Toplevel(self.master)
                self.app = ler_digital_window(self.newWindow)
                self.thread_leitura = threading.Thread(target=registrar_entrada_saida,
                                                    kwargs={'callback': self.app.retorno_busca_biometrica})
                self.thread_leitura.start()

        def comando_cadastrar_novo_usuario(self):
                if isinstance(self.app,cadastrar_novo_usuario_window):
                    self.app.finalizar_janela()
                self.newWindow = tk.Toplevel(self.master)
                self.app = cadastrar_novo_usuario_window(self.newWindow)

        def comando_liberar_entrada_saida_manualmente(self):
                self.newWindow = tk.Toplevel(self.master)
                self.app = windowclass3(self.newWindow)

        def comando_sair_do_sistema(self):
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

        #Método que funciona como uma forma de CALLBACK da thread que realiza a leitura da impressão digital
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
        self.finalizar_janela()

    def finalizar_janela(self):
        self.master.destroy()
        self.callback()

class cadastrar_novo_usuario_window():
        def __init__(self , master):
                self.master = master
                self.frame = tk.Frame(master)
                master.title("Cadastro de novo usuario")
                self.usernamelbl = Label(master, text="Nome:")
                self.username = Entry(master)
                self.variable = tk.StringVar(master)
                # Como opção DEFAULT, o primeiro campo do dicionário
                default_str = list(posto_graduacao_dict.keys())[0]
                self.variable.set(default_str)
                self.opt = default_str
                self.PGopt = tk.OptionMenu(master, self.variable, *posto_graduacao_dict,command=self.mudanca_opcao_selecao)
                self.PGopt.pack()
                self.OMlbl = Label(master, text="OM:")
                self.OM = Entry(master)
                self.cadastrar_button = tk.Button(self.frame, text = 'Cadastrar', width = 25 , command = self.ler_digital_novo_usuario)
                self.cancel_button = tk.Button(self.frame, text='Cancelar', width = 25, command= self.finalizar_janela)


                self.usernamelbl.pack()
                self.username.pack()
                self.OMlbl.pack()
                self.OM.pack()
                self.cadastrar_button.pack()
                self.cancel_button.pack()
                self.frame.pack()


        def mudanca_opcao_selecao(self,value):
            self.opt = value

        def ler_digital_novo_usuario(self):
                pass


        def finalizar_janela(self):
                self.master.destroy()


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
