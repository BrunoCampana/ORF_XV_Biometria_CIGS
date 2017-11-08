import ctypes
from ctypes import c_char_p

# O tamanho do arquivo de features armazenado para a digital é de 669 bytes
tamanho_buffer_digital = 669
sdk = ctypes.cdll.LoadLibrary("libcis_sdk.so")

# Utilizdo para verificar o tipo de retorno
verificar_retorno_func = sdk.CIS_SDK_Retorno
verificar_retorno_func.restype = c_char_p

def iniciar_leitor():
    # Parametro 0 : sem detecção de dedo falso
    return sdk.CIS_SDK_Biometrico_Iniciar(0)

def ler_digital(dig):
    return sdk.CIS_SDK_Biometrico_LerDigital(dig)

def finalizar_leitor():
    return sdk.CIS_SDK_Biometrico_Finalizar()

def comparar_digitais(dig1,dig2):
    return sdk.CIS_SDK_Biometrico_CompararDigital(dig1,dig2)

def cancelar_leitura():
    return sdk.CIS_SDK_CancelarLeitura()

def verificar_retorno(iRetorno):
    return verificar_retorno_func(iRetorno)
