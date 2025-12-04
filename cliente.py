import socket
import json
import tkinter as tk
from tkinter import messagebox
from threading import Thread, Lock
import time

class ClienteJogoDaVelha:
    def __init__(self, ip_servidor, porta=12111):
        # Configuração de rede
        self.ip_servidor = ip_servidor
        self.porta = porta
        self.cliente = None
        self.conectado = False
        self.tentativas_reconexao = 0
        self.max_tentativas = 5
        
        # Estado do jogo
        self.meu_simbolo = None
        self.turno_atual = 'X'
        self.tabuleiro = [['' for _ in range(3)] for _ in range(3)]
        self.jogo_ativo = False
        self.lock = Lock()
        
        # Buffer para mensagens TCP
        self.buffer = ""
        
        # Interface gráfica
        self.janela = tk.Tk()
        self.janela.title("Jogo da Velha Online")
        self.janela.geometry("400x500")
        self.janela.resizable(False, False)
        self.janela.protocol("WM_DELETE_WINDOW", self.fechar_janela)
        
        self.criar_interface()
        
        # Conectar após criar interface
        self.janela.after(100, self.conectar_servidor)
    
    def criar_interface(self):
        """Cria a interface gráfica do jogo"""
        # Frame superior com informações
        frame_info = tk.Frame(self.janela, bg='#2c3e50', height=80)
        frame_info.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.label_status = tk.Label(
            frame_info,
            text="Conectando ao servidor...",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        self.label_status.pack(pady=10)
        
        self.label_turno = tk.Label(
            frame_info,
            text="",
            font=('Arial', 12),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.label_turno.pack()
        
        # Frame do tabuleiro
        frame_tabuleiro = tk.Frame(self.janela, bg='#34495e')
        frame_tabuleiro.pack(pady=20)
        
        self.botoes = []
        for i in range(3):
            linha_botoes = []
            for j in range(3):
                btn = tk.Button(
                    frame_tabuleiro,
                    text='',
                    font=('Arial', 32, 'bold'),
                    width=5,
                    height=2,
                    bg='#ecf0f1',
                    fg='#2c3e50',
                    activebackground='#bdc3c7',
                    command=lambda linha=i, col=j: self.fazer_jogada(linha, col)
                )
                btn.grid(row=i, column=j, padx=5, pady=5)
                linha_botoes.append(btn)
            self.botoes.append(linha_botoes)
        
        # Botão de reiniciar
        self.btn_reiniciar = tk.Button(
            self.janela,
            text="Novo Jogo",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            command=self.reiniciar_jogo,
            state=tk.DISABLED
        )
        self.btn_reiniciar.pack(pady=10)
        
        # Indicador de conexão
        self.label_conexao = tk.Label(
            self.janela,
            text="● Desconectado",
            font=('Arial', 10),
            fg='#e74c3c'
        )
        self.label_conexao.pack(pady=5)
    
    def conectar_servidor(self):
        """Conecta ao servidor usando TCP"""
        if self.conectado:
            return
        
        try:
            print(f"Conectando ao servidor {self.ip_servidor}:{self.porta}...")
            self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cliente.settimeout(10.0)
            self.cliente.connect((self.ip_servidor, self.porta))
            
            self.conectado = True
            self.tentativas_reconexao = 0
            
            print("✓ Conectado ao servidor!")
            self.atualizar_status("Conectado! Aguardando jogadores...")
            self.label_conexao.config(text="● Conectado", fg='#27ae60')
            
            # Iniciar threads
            Thread(target=self.receber_mensagens, daemon=True).start()
            Thread(target=self.enviar_heartbeat, daemon=True).start()
            
            # Enviar mensagem de conexão
            endereco = f"{self.cliente.getsockname()[0]}:{self.cliente.getsockname()[1]}"
            mensagem = {'tipo': 'CONECTAR', 'endereco': endereco}
            self.enviar_mensagem(mensagem)
            
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            self.conectado = False
            self.tentativas_reconexao += 1
            
            if self.tentativas_reconexao < self.max_tentativas:
                tempo_espera = min(3000 * self.tentativas_reconexao, 10000)
                self.atualizar_status(f"Erro na conexão. Tentando novamente em {tempo_espera//1000}s...")
                self.janela.after(tempo_espera, self.conectar_servidor)
            else:
                self.atualizar_status("Não foi possível conectar ao servidor")
                messagebox.showerror("Erro", "Não foi possível conectar ao servidor após várias tentativas.")
    
    def enviar_heartbeat(self):
        """Envia ping periódico para manter conexão ativa"""
        while self.conectado:
            try:
                time.sleep(5)
                if self.conectado:
                    self.enviar_mensagem({'tipo': 'PING'})
            except:
                break
    
    def enviar_mensagem(self, mensagem):
        """Envia mensagem para o servidor"""
        try:
            if self.cliente and self.conectado:
                dados = json.dumps(mensagem) + '\n'
                self.cliente.sendall(dados.encode())
                print(f"Enviado: {mensagem.get('tipo')}")
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            self.desconectar()
    
    def receber_mensagens(self):
        """Recebe mensagens do servidor continuamente"""
        while self.conectado:
            try:
                dados = self.cliente.recv(4096).decode()
                if not dados:
                    print("Servidor desconectado")
                    self.desconectar()
                    break
                
                self.buffer += dados
                
                # Processar mensagens completas
                while '\n' in self.buffer:
                    linha, self.buffer = self.buffer.split('\n', 1)
                    if linha.strip():
                        mensagem = json.loads(linha)
                        print(f"Recebido: {mensagem.get('tipo')}")
                        
                        # Processar na thread principal
                        self.janela.after(0, self.processar_resposta, mensagem)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.conectado:
                    print(f"Erro ao receber: {e}")
                    self.desconectar()
                break
    
    def desconectar(self):
        """Desconecta do servidor"""
        with self.lock:
            if not self.conectado:
                return
            
            self.conectado = False
            self.jogo_ativo = False
            
            try:
                if self.cliente:
                    self.cliente.close()
            except:
                pass
            
            print("Desconectado do servidor")
            self.janela.after(0, self.atualizar_status, "Desconectado do servidor")
            self.janela.after(0, lambda: self.label_conexao.config(text="● Desconectado", fg='#e74c3c'))
            
            # Tentar reconectar
            if self.tentativas_reconexao < self.max_tentativas:
                self.janela.after(3000, self.conectar_servidor)
    
    def processar_resposta(self, mensagem):
        """Processa resposta do servidor"""
        tipo = mensagem.get('tipo')
        
        if tipo == 'PONG':
            return  # Heartbeat response
        
        elif tipo == 'CONECTADO':
            with self.lock:
                self.meu_simbolo = mensagem.get('simbolo')
                jogadores = mensagem.get('jogadores')
                self.jogo_ativo = mensagem.get('jogo_iniciado', False)
                
                if mensagem.get('tabuleiro'):
                    self.tabuleiro = mensagem.get('tabuleiro')
                    self.atualizar_tabuleiro()
                
                if mensagem.get('turno_atual'):
                    self.turno_atual = mensagem.get('turno_atual')
                
                # Atualizar interface
                if self.jogo_ativo and jogadores == 2:
                    self.atualizar_status(f"Você é: {self.meu_simbolo}")
                    self.atualizar_turno(self.turno_atual)
                    print(f"✓ Jogo iniciado! Você é {self.meu_simbolo}")
                else:
                    self.atualizar_status(f"Você é: {self.meu_simbolo} | Aguardando oponente...")
                    self.label_turno.config(text="")
        
        elif tipo == 'JOGO_INICIADO':
            with self.lock:
                self.meu_simbolo = mensagem.get('simbolo')
                self.jogo_ativo = True
                self.tabuleiro = mensagem.get('tabuleiro')
                self.turno_atual = mensagem.get('turno_atual')
            
            print(f"✓✓✓ JOGO INICIADO! Você é {self.meu_simbolo}")
            self.atualizar_tabuleiro()
            self.atualizar_status(f"Você é: {self.meu_simbolo}")
            self.atualizar_turno(self.turno_atual)
        
        elif tipo == 'JOGADA_OK':
            with self.lock:
                self.tabuleiro = mensagem.get('tabuleiro')
                self.turno_atual = mensagem.get('proximo_turno')
            self.atualizar_tabuleiro()
            self.atualizar_turno(self.turno_atual)
        
        elif tipo == 'FIM_JOGO':
            with self.lock:
                self.tabuleiro = mensagem.get('tabuleiro')
                self.jogo_ativo = False
                ganhador = mensagem.get('ganhador')
            self.atualizar_tabuleiro()
            self.finalizar_jogo(ganhador)
        
        elif tipo == 'ERRO':
            msg = mensagem.get('mensagem')
            print(f"Erro do servidor: {msg}")
            if msg not in ['Não é seu turno', 'Casa ocupada']:
                messagebox.showwarning("Aviso", msg)
        
        elif tipo == 'REINICIO':
            with self.lock:
                self.tabuleiro = mensagem.get('tabuleiro', [['' for _ in range(3)] for _ in range(3)])
                self.jogo_ativo = True
                self.turno_atual = mensagem.get('turno_atual', 'X')
            self.atualizar_tabuleiro()
            self.atualizar_status(f"Você é: {self.meu_simbolo}")
            self.atualizar_turno(self.turno_atual)
            self.btn_reiniciar.config(state=tk.DISABLED)
        
        elif tipo == 'OPONENTE_DESCONECTOU':
            with self.lock:
                self.jogo_ativo = False
                self.tabuleiro = [['' for _ in range(3)] for _ in range(3)]
            self.atualizar_tabuleiro()
            self.atualizar_status("Oponente desconectou - Aguardando novo jogador...")
            self.label_turno.config(text="")
            self.btn_reiniciar.config(state=tk.DISABLED)
            messagebox.showinfo("Aviso", mensagem.get('mensagem'))
    
    def fazer_jogada(self, linha, coluna):
        """Envia jogada para o servidor"""
        with self.lock:
            if not self.conectado:
                messagebox.showinfo("Aviso", "Não conectado ao servidor")
                return
            
            if not self.jogo_ativo:
                messagebox.showinfo("Aguarde", "Aguardando outro jogador...")
                return
            
            if self.turno_atual != self.meu_simbolo:
                return  # Silenciosamente ignora se não é o turno
            
            if self.tabuleiro[linha][coluna] != '':
                return  # Silenciosamente ignora casa ocupada
        
        print(f"Fazendo jogada: ({linha}, {coluna})")
        mensagem = {
            'tipo': 'JOGADA',
            'linha': linha,
            'coluna': coluna
        }
        self.enviar_mensagem(mensagem)
    
    def atualizar_tabuleiro(self):
        """Atualiza a visualização do tabuleiro"""
        for i in range(3):
            for j in range(3):
                valor = self.tabuleiro[i][j]
                self.botoes[i][j].config(
                    text=valor,
                    fg='#e74c3c' if valor == 'X' else '#3498db' if valor == 'O' else '#2c3e50'
                )
    
    def atualizar_status(self, texto):
        """Atualiza o texto de status"""
        self.label_status.config(text=texto)
    
    def atualizar_turno(self, turno):
        """Atualiza informação de turno"""
        if turno == self.meu_simbolo:
            self.label_turno.config(text="SUA VEZ!", fg='#2ecc71')
        else:
            self.label_turno.config(text="Vez do oponente...", fg='#e67e22')
    
    def finalizar_jogo(self, ganhador):
        """Finaliza o jogo e exibe resultado"""
        self.btn_reiniciar.config(state=tk.NORMAL)
        
        if ganhador == 'EMPATE':
            mensagem = "Empate!"
            self.atualizar_status("Jogo empatou!")
        elif ganhador == self.meu_simbolo:
            mensagem = "Você venceu! 🎉"
            self.atualizar_status("VOCÊ VENCEU!")
        else:
            mensagem = "Você perdeu!"
            self.atualizar_status("Você perdeu...")
        
        self.label_turno.config(text="")
        messagebox.showinfo("Fim de Jogo", mensagem)
    
    def reiniciar_jogo(self):
        """Solicita reinício do jogo"""
        if not self.conectado:
            messagebox.showinfo("Aviso", "Não conectado ao servidor")
            return
        
        print("Solicitando reinício do jogo")
        mensagem = {'tipo': 'REINICIAR'}
        self.enviar_mensagem(mensagem)
    
    def fechar_janela(self):
        """Fecha a janela e limpa recursos"""
        with self.lock:
            self.conectado = False
        
        try:
            if self.cliente:
                self.cliente.close()
        except:
            pass
        
        self.janela.destroy()
    
    def iniciar(self):
        """Inicia a interface gráfica"""
        self.janela.mainloop()

if __name__ == '__main__':
    # Configuração
    IP_SERVIDOR = '127.0.0.1'  # Altere para o IP do servidor
    PORTA = 12111
    
    print(f"Iniciando cliente...")
    print(f"Conectando a {IP_SERVIDOR}:{PORTA}")
    
    cliente = ClienteJogoDaVelha(IP_SERVIDOR, PORTA)
    cliente.iniciar()