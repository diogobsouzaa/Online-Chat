## Yudi Asano Ramos - 12873553
## Diogo Barboza de Souza - 12745657

import socket
import threading
import time

# Variáveis globais para rastrear as salas disponíveis
available_rooms = set()

# Função para ler mensagens do servidor
def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                # Se não houver dados, o servidor desconectou
                print('Conexão com o servidor perdida.')
                client_socket.close()
                break
            message = data.decode('utf-8')
            
            # Verifica se uma nova sala foi criada
            if "uma nova sala foi criada!" in message:
                print('Digite "/listar" para ver as novas salas.')
            else:
                print(message)
        except Exception as e:
            print(f'Erro na comunicação com o servidor: {e}')
            client_socket.close()
            break

# Função para verificar novas salas a cada 10 segundos
def check_new_rooms(client):
    while True:
        time.sleep(60)
        client.send('/listar'.encode('utf-8'))

# Endereço IP padrão
HOST = '127.0.0.1'

# Solicitar apenas a porta do servidor
PORT = int(input('Digite a porta do servidor: '))

# Configuração do cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print(f'Conectado ao servidor em {HOST}:{PORT}')

print(f'\nVocê está conectado ao servidor, aqui você pode realizar os seguintes comandos:\n\n/criar "Nome da sala"       .Para criar uma sala.\n/listar                     .Para ver a lista de salas em que pode se conectar.\n/conectar "Nome da sala"    .Para se conectar a uma sala.\n\nAo conectar em uma sala você poderá mandar mensagens aos usuários.\n')

# Inicia uma thread para receber mensagens do servidor
receive_thread = threading.Thread(target=receive_messages, args=(client,))
receive_thread.start()

# Inicia uma thread para verificar novas salas
check_new_rooms_thread = threading.Thread(target=check_new_rooms, args=(client,))
check_new_rooms_thread.start()

# Loop principal para enviar mensagens
while True:
    try:
        mensagem = input()
        if mensagem.startswith('/criar'):
            client.send(mensagem.encode('utf-8'))
        elif mensagem.startswith('/listar'):
            client.send(mensagem.encode('utf-8'))
        elif mensagem.startswith('/conectar'):
            client.send(mensagem.encode('utf-8'))
        else:
            # Apenas envie a mensagem
            client.send(mensagem.encode('utf-8'))
    except KeyboardInterrupt:
        print('Cliente encerrado.')
        client.close()
        break
    except Exception as e:
        print(f'Erro ao enviar mensagem: {e}')
        client.close()
        break

