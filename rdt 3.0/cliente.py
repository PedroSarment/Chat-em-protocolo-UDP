import PySimpleGUI as sg
import socket
import sys
from threading import Thread

MyCard = {
    "name": "Matheus Cabral",
    "address": "localhost",
    "port": 52218
}

ConnectWithCard = {
    "name": "Pedro Henrique",
    "address": "localhost",
    "port": 52219
}
Text = ""

bufferSize = 1024
pacote_size = 65


s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.bind((MyCard['address'], MyCard['port']))


def recebe_Ack():
    s.settimeout(1)
    while True:
        try: 
            data = s.recv(bufferSize)
            return data
        except socket.timeout:
            return False

def complemento(n,tamanho):
	comp = n ^ ((1 << tamanho) - 1)
	return '0b{0:0{1}b}'.format(comp, tamanho)

def fun_checksum(portaorigem,portadestino,comprimento):
	primeirasoma = bin(portaorigem+portadestino)[2:].zfill(16)
	if (len(primeirasoma)>16):
		primeirasoma = primeirasoma[1:17]
		primeirasoma = bin(int(primeirasoma,2) + 1)[2:].zfill(16)
	segundasoma = bin(int(primeirasoma,2)+comprimento)[2:].zfill(16)
	if (len(segundasoma)>16):
		segundasoma = segundasoma[1:17]
		segundasoma = bin(int(segundasoma,2) + 1)[2:].zfill(16)
	checksum = complemento(int(segundasoma,2),16)[2:]
	return int(checksum,2)

def onReceive(data):
    global Text
    mensagem = data.decode()
    Text = Text+ConnectWithCard['name']+": "+mensagem+'\n'
    print(Text)


def sendMessage(mensagem):
    global Text
    bytesToSend = str.encode(mensagem)
    serverAddressPort = (ConnectWithCard['address'], ConnectWithCard['port'])
    try:
        s.sendto(bytesToSend, serverAddressPort)
    except socket.error:
        print('Código do erro:')
        sys.exit()

mensagem = ''

while 1:

    entrada = input()

    #Montando o cabeçalho do pacote: 
    # 16 bytes para todos os campos menos sequência, que só precisa de um. 
    c_porta_origem = str(MyCard['port']).ljust(16, "/")
    c_porta_destino = str(ConnectWithCard['port']).ljust(16, "/")
    c_comprimento_total = str((pacote_size + len(entrada))).ljust(16, "/")
    c_checksum = str(fun_checksum(MyCard['port'], ConnectWithCard['port'], (pacote_size + len(entrada)))).ljust(16, "/")
    c_sequencia = '0'
    c_dado = entrada

    print('porta_origem: '+ c_porta_origem.replace("/","")) 
    print('porta_destin: ' + c_porta_destino.replace("/","")) 
    print('comprimento_total: ' + c_comprimento_total.replace("/",""))
    print('checksum: ' + c_checksum.replace("/","")) 
    print('sequencia: ' + c_sequencia.replace("/",""))
    print('dados: ' + c_dado.replace("/","")) 


    mensagem = c_porta_origem + c_porta_destino + c_comprimento_total + c_checksum + c_sequencia + c_dado
    sendMessage(mensagem)

    
    while True:        
        data = recebe_Ack()
        
        if(data == False):
            print(data)
            sendMessage(mensagem) 
        
        else:      

            pacote = data.decode()

            s_porta_origem = pacote[0:16].replace("/","")
            s_porta_destino = pacote[16:32].replace("/","")
            s_comprimento_total = pacote[32:48].replace("/","")
            s_checksum = pacote[48:64].replace("/","")
            s_sequencia = pacote[64].replace("/","")

            soma_entrada = fun_checksum(int(s_porta_origem), int(s_porta_destino), pacote_size)


            if(s_sequencia == '0' and soma_entrada == int(s_checksum)):
                break             

    entrada = input()

    c_porta_origem = str(MyCard['port']).ljust(16, "/")
    c_porta_destino = str(ConnectWithCard['port']).ljust(16, "/")
    c_comprimento_total = str((pacote_size + len(entrada))).ljust(16, "/")
    c_checksum = str(fun_checksum(MyCard['port'], ConnectWithCard['port'], (pacote_size + len(entrada)))).ljust(16, "/")
    c_sequencia = '1'
    c_dado = entrada

    print('porta_origem: '+ c_porta_origem.replace("/","")) 
    print('porta_destin: ' + c_porta_destino.replace("/","")) 
    print('comprimento_total: ' + c_comprimento_total.replace("/",""))
    print('checksum: ' + c_checksum.replace("/","")) 
    print('sequencia: ' + c_sequencia.replace("/",""))
    print('dados: ' + c_dado.replace("/","")) 


    mensagem = c_porta_origem + c_porta_destino + c_comprimento_total + c_checksum + c_sequencia + c_dado
    sendMessage(mensagem)

    while True:        
        
        data = recebe_Ack()
        
        if(data == False):
            sendMessage(mensagem) 
        
        else:      

            pacote = data.decode()

            s_porta_origem = pacote[0:16].replace("/","")
            s_porta_destino = pacote[16:32].replace("/","")
            s_comprimento_total = pacote[32:48].replace("/","")
            s_checksum = pacote[48:64].replace("/","")
            s_sequencia = pacote[64].replace("/","")

            soma_entrada = fun_checksum(int(s_porta_origem), int(s_porta_destino), pacote_size)


            if(s_sequencia == '1' and soma_entrada == int(s_checksum)):
                break  
    
