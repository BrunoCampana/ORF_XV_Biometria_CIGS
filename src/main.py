from database_methods import *
from biometria import iniciar_leitor,finalizar_leitor

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
    print ("1 - Registrar entrada ou saída.")
    print ("2 - Cadastrar novo usuário")
    print ("3 - Sair do sistema.")

def tratar_opcao(option):
    global done
    if (option == "1"):
        registrar_entrada_saida()
    elif (option == "2"):
        cadastrar_novo_usuario()
    elif (option == "3"):
        done = True
    else:
        print ("[!] Opção inválida.")

def main():
    # Ao iniciar o software, obter do banco de dados as tabelas de TIPO e POSTO_GRADUAÇÃO,
    # e armazená-las em um dicionário global
    obter_postos_graduacoes_e_criar_dicionario()
    obter_tipos_eventos_e_criar_dicionario()
    iniciar_leitor()
    printASCIIArt()
    # Loop principal
    while not done:
        print ("O que voce deseja fazer?")
        printOptions()
        option = input("Opção: ")
        tratar_opcao(option)

    finalizar_leitor()

if __name__ == "__main__":
    main()
