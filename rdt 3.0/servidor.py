import PySimpleGUI as sg
import socket
import sys
from threading import Thread

MyCard = {
    "name": "Pedro Henrique",
    "address": "localhost",
    "port": 52219
}

ConnectWithCard = {
    "name": "Matheus Cabral",
    "address": "localhost",
    "port": 52218

}

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.bind((MyCard['address'], MyCard['port']))

bufferSize = 10240
s_pacote_size = 65

Text = ""

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


while True:

    data = s.recv(bufferSize)
    pacote = data.decode()

    porta_origem = pacote[0:16].replace("/","")
    porta_destino = pacote[16:32].replace("/","")
    comprimento_total = pacote[32:48].replace("/","")
    checksum = pacote[48:64].replace("/","")
    sequencia = pacote[64].replace("/","")
    dados = pacote[65:]


    print('porta_origem: '+ porta_origem) 
    print('porta_destin: ' + porta_destino) 
    print('comprimento_total: ' +comprimento_total)
    print('checksum: ' + checksum) 
    print('sequencia: ' + sequencia)
    print('dados: ' + dados) 

    soma_entrada = fun_checksum(int(porta_origem), int(porta_destino), int(comprimento_total))

    if(sequencia != '0' or soma_entrada != int(checksum)):
        s_porta_origem = str(MyCard['port']).ljust(16, "/")
        s_porta_destino = porta_origem.ljust(16, "/")
        s_comprimento_total = str(s_pacote_size).ljust(16, "/")
        s_checksum = str(fun_checksum(int(MyCard['port']), int(porta_origem), s_pacote_size)).ljust(16, "/")
        s_sequencia = '1'
    else: 
        s_porta_origem = str(MyCard['port']).ljust(16, "/")
        s_porta_destino = porta_origem.ljust(16, "/")
        s_comprimento_total = str(s_pacote_size).ljust(16, "/")
        s_checksum = str(fun_checksum(int(MyCard['port']), int(porta_origem), s_pacote_size)).ljust(16, "/")
        s_sequencia = '0'
    
    mensagem = s_porta_origem + s_porta_destino + s_comprimento_total + s_checksum + s_sequencia
    sendMessage(mensagem)

    data = s.recv(bufferSize)
    pacote = data.decode()

    porta_origem = pacote[0:16].replace("/","")
    porta_destino = pacote[16:32].replace("/","")
    comprimento_total = pacote[32:48].replace("/","")
    checksum = pacote[48:64].replace("/","")
    sequencia = pacote[64].replace("/","")
    dados = pacote[65:]

    print('porta_origem: '+ porta_origem) 
    print('porta_destin: ' + porta_destino) 
    print('comprimento_total: ' +comprimento_total)
    print('checksum: ' +checksum) 
    print('sequencia: ' +sequencia)
    print('dados: ' +dados) 

    soma_entrada = fun_checksum(int(porta_origem), int(porta_destino), int(comprimento_total))

    if(sequencia != '1' or soma_entrada != int(checksum)):
        s_porta_origem = str(MyCard['port']).ljust(16, "/")
        s_porta_destino = porta_origem.ljust(16, "/")
        s_comprimento_total = str(s_pacote_size).ljust(16, "/")
        s_checksum = str(fun_checksum(int(MyCard['port']), int(porta_origem), s_pacote_size)).ljust(16, "/")
        s_sequencia = '0'
    else: 
        s_porta_origem = str(MyCard['port']).ljust(16, "/")
        s_porta_destino = porta_origem.ljust(16, "/")
        s_comprimento_total = str(s_pacote_size).ljust(16, "/")
        s_checksum = str(fun_checksum(int(MyCard['port']), int(porta_origem), s_pacote_size)).ljust(16, "/")
        s_sequencia = '1'
        print(dados) 
    
    mensagem = s_porta_origem + s_porta_destino + s_comprimento_total + s_checksum + s_sequencia
    sendMessage(mensagem)











