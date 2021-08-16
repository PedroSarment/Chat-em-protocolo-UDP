import PySimpleGUI as sg
import socket
import sys
from threading import Thread

MyCard = {
    "name": "Matheus Cabral",
    "address": "127.0.0.1",
    "port": 20001
}

ConnectWithCard = {
    "name": "Pedro Henrique",
    "address": "127.0.0.1",
    "port": 20002
}

bufferSize = 1024

# Create a UDP socket at client side

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.bind((MyCard['address'], MyCard['port']))

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
Text = ""
layout = [  [sg.Text('Chat:')],
            [sg.Multiline(default_text=Text, size=(70, 20),key='textbox', disabled=True)],
            [sg.Text('Digite a mensagem a ser enviada:')],
            [sg.InputText(size=(70, 1), focus=True, key='message')],
            [sg.Button('Enviar'), sg.Button('Sair')]]

# Create the Window
window = sg.Window(MyCard['name'], layout, finalize=True)

# Event Loop to process "events" and get the "values" of the inputs

def onReceive(data):
    global Text
    mensagem = data.decode()
    Text = Text+ConnectWithCard['name']+": "+mensagem+'\n'
    window['textbox'].update(Text)

def sendMessage(mensagem):
    global Text
    bytesToSend = str.encode(mensagem)
    serverAddressPort = (ConnectWithCard['address'], ConnectWithCard['port'])
    s.sendto(bytesToSend, serverAddressPort)
    Text = Text + MyCard['name'] + ': ' + mensagem + '\n'
    window['textbox'].update(Text)
    window['message'].update('')

def recv():
    while True:
         data = s.recv(bufferSize)
         if not data: sys.exit(0)
         onReceive(data)

Thread(target=recv).start()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Sair': # if user closes window or clicks cancel
        break
    sendMessage(values['message'])




window.close()
