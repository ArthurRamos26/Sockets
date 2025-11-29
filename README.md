# 🎮 Jogo da Velha com Sockets em Python

Um projeto de jogo da velha (Tic Tac Toe) implementado em Python utilizando **sockets TCP/IP** para comunicação em rede entre dois jogadores remotos.

## 📋 Descrição

Este projeto demonstra a implementação de uma aplicação cliente-servidor em Python, onde dois jogadores podem se conectar via rede e jogar uma partida de jogo da velha em tempo real. A comunicação entre os jogadores é feita através de **sockets TCP**, permitindo que os jogadores estejam em máquinas diferentes.

## ✨ Características

- 🎯 **Comunicação em Rede**: Implementação usando sockets TCP/IP
- 👥 **Multiplayer**: Suporta 2 jogadores conectados remotamente
- 🔄 **Turnos Alternados**: Controle automático de turno entre jogadores
- 📊 **Validação de Movimentos**: Verifica jogadas inválidas
- 🏆 **Detecção de Vitória**: Identifica vencedor ou empate
- 🖥️ **Interface no Terminal**: Interação simples via linha de comando

## 🛠️ Requisitos

- **Python** 3.7 ou superior
- **Sistema Operacional**: Windows, macOS ou Linux
- Sem dependências externas (usa apenas bibliotecas padrão do Python)

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/ArthurRamos26/Sockets.git
cd "Jogo Da Velha"
```

2. Não há dependências externas para instalar. O projeto usa apenas módulos padrão do Python.

## 🚀 Como Usar

### 1. Inicie o Servidor

Em um terminal, execute:

```bash
python jogo-da-velha.py server
```

O servidor aguardará conexões na porta padrão (geralmente `5000`).

### 2. Conecte o Primeiro Jogador

Em outro terminal (ou máquina), execute:

```bash
python jogo-da-velha.py client localhost 5000
```

Ou se estiver em uma máquina diferente:

```bash
python jogo-da-velha.py client <IP_DO_SERVIDOR> 5000
```

### 3. Conecte o Segundo Jogador

Em um terceiro terminal, execute o mesmo comando do primeiro jogador. Quando dois jogadores estiverem conectados, o jogo começará automaticamente.

### 4. Jogue

- Os jogadores serão informados de qual símbolo usarão (X ou O)
- O primeiro jogador sempre começa (X)
- Digite a posição do tabuleiro (1-9) para fazer sua jogada:

```
 1 | 2 | 3
-----------
 4 | 5 | 6
-----------
 7 | 8 | 9
```

- O jogo continua até que um jogador vença ou haja empate

## 📐 Arquitetura

### Componentes Principais

```
┌─────────────────┐          ┌──────────────┐          ┌─────────────────┐
│  Cliente 1 (X)  │◄────────►│   Servidor   │◄────────►│  Cliente 2 (O)  │
│   (Sockets)     │ TCP/IP   │  (Sockets)   │  TCP/IP  │   (Sockets)     │
└─────────────────┘          └──────────────┘          └─────────────────┘
```

### Protocolo de Comunicação

O servidor gerencia:
- **Conexões**: Aceita até 2 clientes
- **Turnos**: Controla qual jogador pode jogar
- **Validação**: Verifica jogadas válidas
- **Sincronização**: Mantém ambos os clientes sincronizados com o estado do jogo

## 🎮 Exemplo de Uso

```bash
# Terminal 1 - Servidor
$ python jogo-da-velha.py server
[Servidor iniciado] Aguardando conexões...
[Cliente conectado] 127.0.0.1:54321
[Cliente conectado] 127.0.0.1:54322
[Jogo iniciado] Duas conexões estabelecidas

# Terminal 2 - Jogador 1
$ python jogo-da-velha.py client localhost 5000
Conectado ao servidor
Você é o jogador: X
É a sua vez!
Digite uma posição (1-9): 5
   |   |   
-----------
   | X |   
-----------
   |   |   
Aguardando o outro jogador...

# Terminal 3 - Jogador 2
$ python jogo-da-velha.py client localhost 5000
Conectado ao servidor
Você é o jogador: O
Aguardando sua vez...
É a sua vez!
Digite uma posição (1-9): 1
 O |   |   
-----------
   | X |   
-----------
   |   |   
Aguardando o outro jogador...
```

## 📝 Estrutura do Projeto

```
Jogo Da Velha/
├── jogo-da-velha.py      # Arquivo principal do projeto
├── README.md             # Este arquivo
└── sockets.txt           # Informações adicionais sobre sockets
```

## 🔐 Segurança

- ⚠️ Este é um projeto educacional
- Para uso em produção, considere adicionar:
  - Autenticação de usuários
  - Criptografia de comunicação (TLS/SSL)
  - Tratamento robusto de exceções
  - Validação de dados mais rigorosa

## 🐛 Possíveis Erros

| Erro | Solução |
|------|---------|
| `Connection refused` | Certifique-se de que o servidor está rodando |
| `Address already in use` | Aguarde alguns segundos ou mude a porta |
| `Connection reset by peer` | O outro jogador desconectou |
| `Invalid move` | A posição já foi usada ou está fora do intervalo |

## 📚 Conceitos Aprendidos

- ✓ Programação com Sockets TCP/IP
- ✓ Arquitetura Cliente-Servidor
- ✓ Comunicação em Rede
- ✓ Processamento de mensagens
- ✓ Sincronização entre processos
- ✓ Tratamento de conexões simultâneas

## 🎓 Contexto Acadêmico

Este projeto foi desenvolvido como parte do curso de **Redes de Computadores II** da Universidade Federal de Roraima (UFRR).

## 💡 Possíveis Melhorias

- [ ] Interface gráfica (tkinter ou PyGame)
- [ ] Suporte a mais de 2 jogadores
- [ ] Sistema de ranking
- [ ] Histórico de partidas
- [ ] Criptografia de mensagens
- [ ] Reconnection automática
- [ ] Modo espectador

## 📞 Contato

**Autor**: Arthur Ramos  
**GitHub**: [@ArthurRamos26](https://github.com/ArthurRamos26)  
**Repositório**: [Sockets](https://github.com/ArthurRamos26/Sockets)

## 📄 Licença

Este projeto é de código aberto e está disponível para fins educacionais.

---

**Última atualização**: 29 de novembro de 2025
