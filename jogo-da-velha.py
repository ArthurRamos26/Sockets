import socket

ip_jogador = " " 
ip_servidor = " "

server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #Esse soch digram serve para declara como sendo UDP se fosse tcp seria socket_STREAM AFINET É IPV4       
server.bind ('','12111')# ja que o servidor será a prórpria máquina de forma local deixei a parte de escolher o local vazia ea porta escolhida foi a 12111
jogador = socket.socket(socket.AF_INET,socket.SOCK_DIAGRAM)
#Tive que declarar fora pois vou precisar para as funções 

def receber_escolha():

    while True:
        escolha_bytes , endereço_sender = server.recvfrom(2048)#2048 é o tamanho padrao 
        escolha = escolha_bytes.decode()#para transformar de bytes para escolha 
        
        if verificar_casa() == None:
            mensagem = ("A sua escolha foi salva")
        else :
            mensagem = ("O lugar que você escolheu já esta em uso ")
        
        server.sendto(mensagem.encode(),ip_jogador)
        
def mandar_escolha():
    escolha = input("Digite 1 para X e 2 para O ")
    jogador.sendto(escolha.encode(),ip_servidor,12111)#A porta que eu escolhi antes  na criação e o encode e pois ele manda em bytes 

def verificar_casa():
 

def verificar_ganhador():

    
def começar_jogo():

def criar_tabuleiro():
