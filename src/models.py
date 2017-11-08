class Usuario:
    def __init__(self):
        self.id = 0
        self.nome = 'Sem Nome'
        self.Cod_PG = 0
        self.OM = 'Sem OM'
        self.Biometria = None

class Evento:
    def __init__(self):
        self.id = 0
        self.id_usuario = 0
        self.id_tipo = 0
        self.data = None

#Os tipos possíveis até agora são : ENTRADA (1) / SAÍDA (2)
class Tipo:
    def __init__(self):
        self.id = 0
        self.tipo = 'Sem Descrição'

class Posto_Graduaçao:
        def __init__(self):
            self.id = 0
            self.PG = 'Sem Descrição'
