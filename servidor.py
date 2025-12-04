import socket
import json
import time
from threading import Thread, Lock
from datetime import datetime, timedelta

class ServidorJogoDaVelha:
    def __init__(self, porta=12111):
        self.porta = porta
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', porta))
        self.server.listen(2)
        
        self.tabuleiro = [['' for _ in range(3)] for _ in range(3)]
        self.jogadores = {}  # {conn: {'simbolo': 'X'/'O', 'ultimo_ping': datetime, 'endereco': addr}}
        self.turno_atual = 'X'
        self.jogo_ativo = False
        self.lock = Lock()
        self.rodando = True
        
        print(f"Servidor TCP iniciado na porta {porta}")
        print("Aguardando jogadores...")
        
        # Inicia thread de monitoramento de conexões
        Thread(target=self.monitorar_conexoes, daemon=True).start()
    
    def monitorar_conexoes(self):
        """Monitora heartbeat dos jogadores e remove inativos"""
        while self.rodando:
            time.sleep(5)
            with self.lock:
                desconectados = []
                agora = datetime.now()
                
                for conn, dados in list(self.jogadores.items()):
                    # Se não recebeu ping há mais de 15 segundos, desconectar
                    if agora - dados['ultimo_ping'] > timedelta(seconds=15):
                        print(f"⚠ Jogador {dados['simbolo']} ({dados['endereco']}) desconectado por timeout")
                        desconectados.append(conn)
                
                for conn in desconectados:
                    self.remover_jogador(conn)
    
    def remover_jogador(self, conn):
        """Remove um jogador e notifica o outro"""
        if conn in self.jogadores:
            simbolo = self.jogadores[conn]['simbolo']
            del self.jogadores[conn]
            
            try:
                conn.close()
            except:
                pass
            
            print(f"✗ Jogador {simbolo} removido. Jogadores restantes: {len(self.jogadores)}")
            
            # Se havia jogo ativo, finalizar
            if self.jogo_ativo:
                self.jogo_ativo = False
                print(f"Jogo cancelado - jogador {simbolo} desconectou")
                
                # Notificar jogador restante
                self.broadcast({
                    'tipo': 'OPONENTE_DESCONECTOU',
                    'mensagem': 'Oponente desconectou. Aguardando novo jogador...'
                })
                
                # Resetar tabuleiro
                self.tabuleiro = [['' for _ in range(3)] for _ in range(3)]
                self.turno_atual = 'X'
    
    def criar_tabuleiro(self):
        """Reinicia o tabuleiro"""
        self.tabuleiro = [['' for _ in range(3)] for _ in range(3)]
        self.turno_atual = 'X'
        self.jogo_ativo = True
        print("\n" + "="*50)
        print("NOVO JOGO INICIADO!")
        print("="*50)
        self.imprimir_tabuleiro()
    
    def verificar_casa(self, linha, coluna):
        """Verifica se a casa está vazia (sem lock - deve ser chamado dentro de lock)"""
        if 0 <= linha < 3 and 0 <= coluna < 3:
            return self.tabuleiro[linha][coluna] == ''
        return False
    
    def imprimir_tabuleiro(self):
        """Imprime o tabuleiro no terminal do servidor"""
        print("\nTabuleiro atual:")
        for i, linha in enumerate(self.tabuleiro):
            linha_str = " | ".join([celula if celula else ' ' for celula in linha])
            print(f"  {linha_str}")
            if i < 2:
                print("  ---------")
        print()
    
    def verificar_ganhador(self):
        """Verifica se há um ganhador ou empate (sem lock - chamar dentro de lock)"""
        # Verifica linhas
        for linha in self.tabuleiro:
            if linha[0] == linha[1] == linha[2] != '':
                return linha[0]
        
        # Verifica colunas
        for col in range(3):
            if self.tabuleiro[0][col] == self.tabuleiro[1][col] == self.tabuleiro[2][col] != '':
                return self.tabuleiro[0][col]
        
        # Verifica diagonais
        if self.tabuleiro[0][0] == self.tabuleiro[1][1] == self.tabuleiro[2][2] != '':
            return self.tabuleiro[0][0]
        
        if self.tabuleiro[0][2] == self.tabuleiro[1][1] == self.tabuleiro[2][0] != '':
            return self.tabuleiro[0][2]
        
        # Verifica empate
        if all(self.tabuleiro[i][j] != '' for i in range(3) for j in range(3)):
            return 'EMPATE'
        
        return None
    
    def processar_mensagem(self, mensagem, conn):
        """Processa mensagens recebidas dos clientes"""
        try:
            tipo = mensagem.get('tipo')
            
            if tipo == 'PING':
                with self.lock:
                    if conn in self.jogadores:
                        self.jogadores[conn]['ultimo_ping'] = datetime.now()
                return {'tipo': 'PONG'}
            
            elif tipo == 'CONECTAR':
                return self.processar_conexao(conn, mensagem.get('endereco'))
            
            elif tipo == 'JOGADA':
                return self.processar_jogada(mensagem, conn)
            
            elif tipo == 'REINICIAR':
                with self.lock:
                    if len(self.jogadores) == 2:
                        self.criar_tabuleiro()
                        resposta = {
                            'tipo': 'REINICIO',
                            'tabuleiro': self.tabuleiro,
                            'turno_atual': self.turno_atual
                        }
                        # Notificar todos
                        self.broadcast(resposta)
                        return resposta
                    else:
                        return {'tipo': 'ERRO', 'mensagem': 'Aguarde outro jogador'}
            
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
            import traceback
            traceback.print_exc()
            return {'tipo': 'ERRO', 'mensagem': str(e)}
    
    def processar_conexao(self, conn, endereco):
        """Processa a conexão de um novo jogador"""
        with self.lock:
            print(f"\n>>> Processando conexão de {endereco}")
            print(f">>> Jogadores atuais: {len(self.jogadores)}")
            print(f">>> Conexão já registrada? {conn in self.jogadores}")
            
            # Se essa conexão já está registrada, apenas atualizar
            if conn in self.jogadores:
                print(f">>> Jogador já conectado, atualizando ping")
                self.jogadores[conn]['ultimo_ping'] = datetime.now()
                return {
                    'tipo': 'CONECTADO',
                    'simbolo': self.jogadores[conn]['simbolo'],
                    'jogadores': len(self.jogadores),
                    'jogo_iniciado': self.jogo_ativo,
                    'tabuleiro': self.tabuleiro,
                    'turno_atual': self.turno_atual
                }
            
            # Verificar se a sala está cheia
            if len(self.jogadores) >= 2:
                print(f">>> SALA CHEIA! Rejeitando nova conexão")
                return {'tipo': 'ERRO', 'mensagem': 'Sala cheia'}
            
            # Registrar novo jogador
            simbolo = 'X' if len(self.jogadores) == 0 else 'O'
            self.jogadores[conn] = {
                'simbolo': simbolo,
                'ultimo_ping': datetime.now(),
                'endereco': endereco
            }
            print(f">>> ✓ Jogador {simbolo} registrado! Total: {len(self.jogadores)}/2")
            
            resposta = {
                'tipo': 'CONECTADO',
                'simbolo': simbolo,
                'jogadores': len(self.jogadores),
                'jogo_iniciado': False,
                'tabuleiro': self.tabuleiro,
                'turno_atual': self.turno_atual
            }
            
            # Se agora temos 2 jogadores, iniciar o jogo
            if len(self.jogadores) == 2:
                print("\n" + "="*50)
                print("✓✓✓ DOIS JOGADORES CONECTADOS! INICIANDO JOGO ✓✓✓")
                print("="*50 + "\n")
                self.criar_tabuleiro()
                
                # Atualizar resposta
                resposta['jogo_iniciado'] = True
                resposta['tabuleiro'] = self.tabuleiro
                resposta['turno_atual'] = self.turno_atual
                
                # Notificar o outro jogador
                for c, dados in self.jogadores.items():
                    if c != conn:
                        notificacao = {
                            'tipo': 'JOGO_INICIADO',
                            'simbolo': dados['simbolo'],
                            'jogadores': 2,
                            'jogo_iniciado': True,
                            'tabuleiro': self.tabuleiro,
                            'turno_atual': self.turno_atual
                        }
                        print(f">>> Notificando jogador {dados['simbolo']} que o jogo começou")
                        self.enviar_mensagem(c, notificacao)
            
            return resposta
    
    def processar_jogada(self, mensagem, conn):
        """Processa uma jogada do cliente - TODA A LÓGICA DENTRO DO LOCK"""
        with self.lock:
            # Verificações de estado
            if not self.jogo_ativo:
                return {'tipo': 'ERRO', 'mensagem': 'Aguarde outro jogador'}
            
            if conn not in self.jogadores:
                return {'tipo': 'ERRO', 'mensagem': 'Você não está registrado'}
            
            simbolo_jogador = self.jogadores[conn]['simbolo']
            
            if simbolo_jogador != self.turno_atual:
                return {'tipo': 'ERRO', 'mensagem': 'Não é seu turno'}
            
            linha = mensagem.get('linha')
            coluna = mensagem.get('coluna')
            
            if linha is None or coluna is None:
                return {'tipo': 'ERRO', 'mensagem': 'Jogada inválida'}
            
            # Verificar se casa está vazia
            if not self.verificar_casa(linha, coluna):
                return {'tipo': 'ERRO', 'mensagem': 'Casa ocupada'}
            
            # Fazer jogada
            self.tabuleiro[linha][coluna] = simbolo_jogador
            print(f"Jogada: {simbolo_jogador} na posição ({linha}, {coluna})")
            self.imprimir_tabuleiro()
            
            # Atualizar ping
            self.jogadores[conn]['ultimo_ping'] = datetime.now()
            
            # Verificar fim de jogo
            ganhador = self.verificar_ganhador()
            
            if ganhador:
                self.jogo_ativo = False
                print(f"\n{'='*50}")
                print(f"JOGO FINALIZADO! Resultado: {ganhador}")
                print(f"{'='*50}\n")
                
                resposta = {
                    'tipo': 'FIM_JOGO',
                    'tabuleiro': self.tabuleiro,
                    'ganhador': ganhador
                }
                
                # Notificar todos
                self.broadcast(resposta)
                return resposta
            
            # Alternar turno
            self.turno_atual = 'O' if self.turno_atual == 'X' else 'X'
            
            resposta = {
                'tipo': 'JOGADA_OK',
                'tabuleiro': self.tabuleiro,
                'proximo_turno': self.turno_atual
            }
            
            # Notificar todos
            self.broadcast(resposta)
            return resposta
    
    def enviar_mensagem(self, conn, mensagem):
        """Envia mensagem para um cliente específico"""
        try:
            dados = json.dumps(mensagem) + '\n'
            conn.sendall(dados.encode())
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            with self.lock:
                if conn in self.jogadores:
                    self.remover_jogador(conn)
    
    def broadcast(self, mensagem):
        """Envia mensagem para todos os jogadores"""
        with self.lock:
            jogadores_copia = list(self.jogadores.keys())
        
        for conn in jogadores_copia:
            self.enviar_mensagem(conn, mensagem)
    
    def handle_cliente(self, conn, addr):
        """Gerencia a comunicação com um cliente"""
        print(f"\n{'='*50}")
        print(f"NOVA CONEXÃO TCP ACEITA de {addr}")
        print(f"{'='*50}\n")
        buffer = ""
        
        try:
            while self.rodando:
                dados = conn.recv(4096)
                if not dados:
                    print(f"Cliente {addr} fechou a conexão")
                    break
                
                buffer += dados.decode()
                
                # Processar mensagens completas (delimitadas por \n)
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    if linha.strip():
                        try:
                            mensagem = json.loads(linha)
                            tipo = mensagem.get('tipo')
                            
                            if tipo != 'PING':  # Não logar PING para não poluir
                                print(f"← Recebido de {addr}: {tipo}")
                            
                            resposta = self.processar_mensagem(mensagem, conn)
                            
                            if resposta:
                                if resposta.get('tipo') != 'PONG':
                                    print(f"→ Enviando para {addr}: {resposta.get('tipo')}")
                                self.enviar_mensagem(conn, resposta)
                        except json.JSONDecodeError as e:
                            print(f"Erro ao decodificar JSON: {e}")
                            print(f"Linha recebida: {linha}")
        
        except Exception as e:
            print(f"Erro na conexão com {addr}: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            print(f"\n{'='*50}")
            print(f"CONEXÃO ENCERRADA: {addr}")
            print(f"{'='*50}\n")
            with self.lock:
                if conn in self.jogadores:
                    self.remover_jogador(conn)
    
    def iniciar(self):
        """Inicia o loop principal do servidor"""
        print("\n" + "="*50)
        print("SERVIDOR RODANDO E AGUARDANDO CONEXÕES")
        print("="*50 + "\n")
        
        try:
            while self.rodando:
                try:
                    conn, addr = self.server.accept()
                    thread = Thread(target=self.handle_cliente, args=(conn, addr), daemon=True)
                    thread.start()
                except Exception as e:
                    if self.rodando:
                        print(f"Erro ao aceitar conexão: {e}")
        
        except KeyboardInterrupt:
            print("\nEncerrando servidor...")
        
        finally:
            self.rodando = False
            self.server.close()

if __name__ == '__main__':
    servidor = ServidorJogoDaVelha()
    servidor.iniciar()