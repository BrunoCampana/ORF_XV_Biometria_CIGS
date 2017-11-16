from database_methods import *
from biometria import iniciar_leitor,finalizar_leitor
from gui import *

import sys

#Variável global que indica o encerramento do programa
done = False

#Creditos:http://patorjk.com/software/taag/
def printASCIIArt():
    print("""
 $$$$$$\  $$\                  $$$$$$\  $$$$$$$$\ $$\   $$\    $$\  $$$$$$
$$  __$$\ \__|                $$  __$$\ $$  _____|$$ |  $$ |   $$ |$$  __$$
$$ /  \__|$$\  $$$$$$$\       $$ /  \__|$$ |      $$ |  $$ |   $$ |$$ /  $$ |
\$$$$$$\  $$ |$$  _____|      \$$$$$$\  $$$$$\    $$ |  \$$\  $$  |$$$$$$$$ |
 \____$$\ $$ |\$$$$$$\         \____$$\ $$  __|   $$ |   \$$\$$  / $$  __$$ |
$$\   $$ |$$ | \____$$\       $$\   $$ |$$ |      $$ |    \$$$  /  $$ |  $$ |
\$$$$$$  |$$ |$$$$$$$  |      \$$$$$$  |$$$$$$$$\ $$$$$$$$\\$  /   $$ |  $$ |
 \______/ \__|\_______/        \______/ \________|\________|\_/    \__|  \__|


                                                                             """)

def printOptions():
    print ("1 - Registrar entrada ou saída por biometria.")
    print ("2 - Cadastrar novo usuário")
    print ("3 - Liberar entrada ou saída manualmente")
    print ("4 - Sair do sistema.")

def tratar_opcao(option):
    global done
    if (option == "1"):
        registrar_entrada_saida()
    elif (option == "2"):
        cadastrar_novo_usuario()
    elif (option == "3"):
        liberar_entrada_saida_manualmente()
    elif (option == "4"):
        done = True
    else:
        print ("[!] Opção inválida.")


class main_class():
    def finalizar_janela(self):
        if isinstance(self.cls.app,ler_digital_window):
            cancelar_leitura()
            self.cls.thread_leitura.join()
            finalizar_leitor()
        self.root.destroy()

    def main_loop_cli(self):
        # Ao iniciar o software, obter do banco de dados as tabelas de TIPO e POSTO_GRADUAÇÃO,
        # e armazená-las em um dicionário global
        obter_postos_graduacoes_e_criar_dicionario()
        obter_tipos_eventos_e_criar_dicionario()
        obter_missoes_e_criar_dicionario()

        iniciar_leitor()
        printASCIIArt()
        # Loop principal
        while not done:
            print ("O que voce deseja fazer?")
            printOptions()
            option = input("Opção: ")
            tratar_opcao(option)

        finalizar_leitor()

    def main_loop_gui(self):
        obter_postos_graduacoes_e_criar_dicionario()
        obter_tipos_eventos_e_criar_dicionario()
        obter_tipos_missoes_e_criar_dicionario()
        finalizar_leitor()

        iRet = iniciar_leitor()
        if iRet != 1:
            messagebox.showinfo("Erro", verificar_retorno(iRet), icon="error")
            return
        self.root = Tk()
        self.root.title("Principal")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW",self.finalizar_janela)
        self.cls = main_window(self.root)
        self.root.mainloop()
        finalizar_leitor()

if __name__ == "__main__":
    printASCIIArt()
    main_class().main_loop_gui()
