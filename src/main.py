from database_methods import *
from biometria import iniciar_leitor,finalizar_leitor

#Variável global que indica o encerramento do programa
done = False

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
    iniciar_leitor()
    #Loop principal
    while not done:
        print ("O que voce deseja fazer?")
        printOptions()
        option = input("Opção: ")
        tratar_opcao(option)

    finalizar_leitor()

if __name__ == "__main__":
    main()
