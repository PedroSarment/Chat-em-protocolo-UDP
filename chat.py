import PySimpleGUI as sg
import socket
import sys
from threading import Thread
from io import StringIO
import time

MyCard = {

    "address": "127.0.0.1",

}

ConnectWithCard = {
}

bufferSize = 1024
s_pacote_size = 66
pacote_size = 66

# Create a UDP socket at client side

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
Text = {}
contactList = []
cards = {}
seqs = {}
seqsend = {}
buffer = {}
alias = {}

def resetMe(destination):
    c_porta_origem = str(MyCard['port']).ljust(16, "/")
    c_porta_destino = str(destination[1]).ljust(16, "/")
    c_comprimento_total = str(s_pacote_size).ljust(16, "/")
    c_checksum = str(fun_checksum(int(MyCard['port']), int(destination[1]), (s_pacote_size))).ljust(
        16, "/")
    way = "3"
    c_sequencia = "0"

    mensagem = c_porta_origem + c_porta_destino + c_comprimento_total + c_checksum + way + c_sequencia

    bytesToSend = str.encode(mensagem)
    serverAddressPort = destination
    for i in range (0, 2):
        s.sendto(bytesToSend, serverAddressPort)

def resetUser(source):
    origem = source[0]+':'+source[1]
    seqsend[origem] = 0
    seqs[origem] = 0

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

def adicionarContato(nome, ip, porta):
    global cards
    global Text
    global seqsend
    global alias

    try:
        int(porta)
        if (int(porta) > 65535):
            return ("Porta maior que 65535!")
    except:
        return ("Porta precisa ser um número!!")
    if (nome not in cards):
        try:
            socket.inet_aton(ip)
            # legal
        except socket.error:
            return ("Ip inválido!!")
            # Not legal
        sg.Popup(nome+' adicionado com sucesso!')
        cards[nome] = {"address": ip,
                       "port": porta}
        if((ip+":"+porta) not in Text):
            Text[ip+":"+porta] = ""
        if ((ip + ":" + porta) not in seqsend):
            seqsend[ip + ":" + porta] = 0
        alias[ip + ":" + porta] = nome
        resetMe((ip, int(porta)))
        return 1
    else:
        return ("Já existe um contato com esse nome!")


layoutChat = [  [sg.Text('Chat:')],
            [sg.Multiline(default_text="", size=(70, 20),key='textbox', disabled=True)],
            [sg.Text('Digite a mensagem a ser enviada:')],
            [sg.InputText(size=(70, 1), focus=True, key='message')],
            [sg.Button('Enviar'), sg.Button('Voltar')]]

layoutStarter = [[sg.Text('Seu nome:'), sg.InputText(size=(50, 1), focus=True, key='myname')],
                 [sg.Text('Escolha uma porta:'),sg.InputText(size=(50, 1), key='myport')],
                 [sg.Button('Confirmar')]]

layoutInicial = [[sg.Button('Adicionar contato'),],
                 [sg.Button('Lista de Contatos')],
                 [sg.Button('Sair')]]

layoutAdicionar = [[sg.Text('Nome:'),sg.InputText(size=(50, 1), focus=True, key='name')],
                 [sg.Text('IP:'),sg.InputText(size=(50, 1), key='ip')],
                 [sg.Text('Porta:'),sg.InputText(size=(50, 1), key='port')],
                 [sg.Button('Adicionar'), sg.Button('Cancelar')]]

layoutContatos = [[sg.Listbox(values=contactList,default_values=("" if len(contactList) == 0 else contactList[0]), select_mode = 'single', bind_return_key = False, change_submits= True, size=(30, 10),key = '_lb1_'), sg.Button('-'), sg.Button('+')],
                  [sg.Button('Conectar', key="ConectBt", disabled=(True if len(contactList) == 0 else False)), sg.Button('Voltar', key="Back")]]

layouts = [[sg.Column(layoutInicial, key='-COL0-', visible=False), sg.Column(layoutChat, visible=False, key='-COL1-'), sg.Column(layoutAdicionar, visible=False, key='-COL2-'), sg.Column(layoutContatos, visible=False, key='-COL3-'), sg.Column(layoutStarter, key='-COL4-')]]


# Create the Window
window = sg.Window("Chat 1.0", layouts, finalize=True, size=(400, 450), element_justification='c')
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
while(True):
    event, values = window.read()
    if ((event == 'Confirmar')):
        MyCard["port"] = int(values["myport"])
        MyCard["name"] = values["myname"]
        try:
            s.bind((MyCard['address'], MyCard['port']))
            atual = 0
            window[f'-COL' + str(atual) + '-'].update(visible=True)
            for i in range(0, len(layouts[0])):
                if (i != atual):
                    window[f'-COL{i}-'].update(visible=False)
            break
        except:
            print("Porta em uso!!!!")
            sg.Popup("Porta em uso!!!!")
    if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
        exit(0)
# Event Loop to process "events" and get the "values" of the inputs

def onReceive(data, origem):
    global Text
    global seqs
    global buffer

    source = origem[0]+":"+str(origem[1])
    pacote = data.decode()

    porta_origem = pacote[0:16].replace("/", "")
    porta_destino = pacote[16:32].replace("/", "")
    comprimento_total = pacote[32:48].replace("/", "")
    checksum = pacote[48:64].replace("/", "")
    way = pacote[64].replace("/", "")
    sequencia = pacote[65].replace("/", "")
    dados = pacote[66:]
    if(way == "1"):
        if (source not in seqs):
            seqs[source] = 0

        soma_entrada = fun_checksum(int(porta_origem), int(porta_destino), int(comprimento_total))

        if((soma_entrada != int(checksum))):
            seqReturn = (1 if int(sequencia) == 0 else 0)
        else:
            seqReturn = sequencia

        s_porta_origem = str(MyCard['port']).ljust(16, "/")
        s_porta_destino = str(origem[1]).ljust(16, "/")
        s_comprimento_total = str(s_pacote_size).ljust(16, "/")
        s_checksum = str(fun_checksum(int(MyCard['port']), int(porta_origem), s_pacote_size)).ljust(16, "/")
        way = "0"
        s_sequencia = str(seqReturn)

        mensagem = s_porta_origem + s_porta_destino + s_comprimento_total + s_checksum + way + s_sequencia
        print(mensagem)
        bytesToSend = str.encode(mensagem)
        s.sendto(bytesToSend, origem)

        if (int(sequencia) == seqs[source]):
            seqs[source] = (1 if int(sequencia) == 0 else 0)
            try:
                name = alias[source]
            except:
                name = source
            if(source not in Text):
                Text[source] = name+":"+dados
            else:
                Text[source] = Text[source]+"\n"+name + ": " + dados
    elif(way == "0"):
        if(source not in buffer):
            buffer[source] = []
        soma_entrada = fun_checksum(int(porta_origem), int(porta_destino), pacote_size)
        s_checksum = pacote[48:64].replace("/", "")
        obj = {
            "soma_entrada": soma_entrada,
            "sequencia": sequencia,
            "s_checksum": s_checksum
        }
        buffer[source].append(obj)
    else:
        soma_entrada = fun_checksum(int(porta_origem), int(porta_destino), int(comprimento_total))

        if (int(sequencia) != 0 and soma_entrada != int(checksum)):
            seqReturn = 1
        else:
            seqReturn = 0
            resetUser(source)

        s_porta_origem = str(MyCard['port']).ljust(16, "/")
        s_porta_destino = str(origem[1]).ljust(16, "/")
        s_comprimento_total = str(s_pacote_size).ljust(16, "/")
        s_checksum = str(fun_checksum(int(MyCard['port']), int(porta_origem), s_pacote_size)).ljust(16, "/")
        way = "0"
        s_sequencia = str(seqReturn)

        mensagem = s_porta_origem + s_porta_destino + s_comprimento_total + s_checksum + way + s_sequencia

        bytesToSend = str.encode(mensagem)
        s.sendto(bytesToSend, origem)

def recebe_Ack(source):
    print("ACK")
    start = time.time()
    try:
        while(True):
            try:
                data = buffer[source][0]
                del buffer[source][0]
                return data
            except:
                if((time.time() - start) > 5):
                    return False
    except:
        return False

def sendMessage(dados):
    global Text
    global seqsend
    c_porta_origem = str(MyCard['port']).ljust(16, "/")
    c_porta_destino = str(ConnectWithCard['port']).ljust(16, "/")
    c_comprimento_total = str((pacote_size + len(dados))).ljust(16, "/")
    c_checksum = str(fun_checksum(int(MyCard['port']), int(ConnectWithCard['port']), (pacote_size + len(dados)))).ljust(16, "/")
    way = "1"
    c_sequencia = str(seqsend[ConnectWithCard['address']+":"+ConnectWithCard['port']])
    c_dado = dados

    mensagem = c_porta_origem + c_porta_destino + c_comprimento_total + c_checksum + way + c_sequencia + c_dado

    bytesToSend = str.encode(mensagem)
    serverAddressPort = (ConnectWithCard['address'], int(ConnectWithCard['port']))

    s.sendto(bytesToSend, serverAddressPort)
    tentativas = 0
    while True:
        data = recebe_Ack(ConnectWithCard['address']+":"+ConnectWithCard['port'])
        print(data)
        if (data == False):
            tentativas += 1
            if(tentativas > 4):
                status = False
                break
            bytesToSend = str.encode(mensagem)
            serverAddressPort = (ConnectWithCard['address'], int(ConnectWithCard['port']))
            s.sendto(bytesToSend, serverAddressPort)

        else:
            soma_entrada = data["soma_entrada"]
            s_checksum = data["s_checksum"]
            s_sequencia = int(data["sequencia"])
            print(s_sequencia == seqsend[ConnectWithCard['address']+":"+ConnectWithCard['port']])
            print(s_sequencia, seqsend[ConnectWithCard['address']+":"+ConnectWithCard['port']])
            print(soma_entrada == int(s_checksum))
            print(soma_entrada, int(s_checksum))
            if (s_sequencia == seqsend[ConnectWithCard['address']+":"+ConnectWithCard['port']] and soma_entrada == int(s_checksum)):
                status = True
                seqsend[ConnectWithCard['address']+":"+ConnectWithCard['port']] = (1 if int(s_sequencia) == 0 else 0)
                break
    if(status):
        window['message'].update('')
        Text[ConnectWithCard['address']+":"+ConnectWithCard['port']] = Text[ConnectWithCard['address']+":"+ConnectWithCard['port']]+"\n"+MyCard['name'] + ": " + dados
    else:
        sg.Popup('Timeout!')
def recv():
    while True:
         data, addr = s.recvfrom(bufferSize)
         if not data: sys.exit(0)
         onReceive(data, addr)


Thread(target=recv).start()
while True:
    event, values = window.read(timeout=1)
    if ((event == 'Enviar')):
        sendMessage(values['message'])
        window['textbox'].update(Text[ConnectWithCard['address']+":"+ConnectWithCard['port']])
    if ((event == 'Adicionar')):
        status = adicionarContato(values['name'], values['ip'], values['port'])
        if(status == 1):
            contactList.append(values['name'])
            window['name'].update("")
            window['ip'].update("")
            window['port'].update("")


            window['_lb1_'].update(contactList)
            window['_lb1_'].update(set_to_index=len(contactList)-1)
            window['ConectBt'].update(disabled=False)
            atual = 3
            window[f'-COL' + str(atual) + '-'].update(visible=True)
            for i in range(0, len(layouts[0])):
                if (i != atual):
                    window[f'-COL{i}-'].update(visible=False)
        else:
            sg.Popup('Error:\n'+status)
    if((event == 'Cancelar' or event == 'Voltar' or event == "Encerrar" or event == "Sair0" or event =="Back")):
        window['name'].update("")
        window['ip'].update("")
        window['port'].update("")
        window.TKroot.title("Chat 1.0")
        ConnectWithCard = []
        if (event == "Encerrar"):
            Text = ""
        atual = 0
        window[f'-COL' + str(atual) + '-'].update(visible=True)
        for i in range(0, len(layouts[0])):
            if (i != atual):
                window[f'-COL{i}-'].update(visible=False)
    elif(event == 'Adicionar contato' or event == '+'):
        atual = 2
        window[f'-COL'+str(atual)+'-'].update(visible=True)
        for i in range(0, len(layouts[0])):
            if(i != atual):
                window[f'-COL{i}-'].update(visible=False)
    elif (event == 'Lista de Contatos'):
        atual = 3
        window[f'-COL' + str(atual) + '-'].update(visible=True)
        for i in range(0, len(layouts[0])):
            if (i != atual):
                window[f'-COL{i}-'].update(visible=False)
    elif (event == 'ConectBt'):

        ConnectWithCard = cards[values['_lb1_'][0]]
        ConnectWithCard["name"] = values['_lb1_'][0]
        window.TKroot.title(values['_lb1_'][0])
        atual = 1
        window[f'-COL' + str(atual) + '-'].update(visible=True)
        window['textbox'].update(Text[ConnectWithCard['address']+":"+ConnectWithCard['port']])
        for i in range(0, len(layouts[0])):
            if (i != atual):
                window[f'-COL{i}-'].update(visible=False)
    elif (event == '-'):
        contactList.remove(values['_lb1_'][0])
        del cards[values['_lb1_'][0]]
        window['_lb1_'].update(contactList)
        window['_lb1_'].update(set_to_index=0)
        window['ConectBt'].update(disabled=(True if len(contactList) == 0 else False))
    elif event == sg.WIN_CLOSED or event == 'Sair': # if user closes window or clicks cancel
        break
    else:
        try:
            window['textbox'].update(Text[ConnectWithCard['address'] + ":" + str(ConnectWithCard['port'])])
        except:
            pass
        #print(event, values)
# while True:
#     event, values = window.read()
#     if event == sg.WIN_CLOSED or event == 'Sair': # if user closes window or clicks cancel
#         break
#     sendMessage(values['message'])




window.close()
