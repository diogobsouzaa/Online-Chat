## Yudi Asano Ramos - 12873553
## Diogo Barboza de Souza - 12745657

import socket
import threading

# Configurações do servidor
host = '127.0.0.1'  # Endereço IP do servidor
port = 12370      # Porta a ser usada pelo servidor

def find_available_port(host, port, max_attempts=10):
    for attempt in range(max_attempts):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.close()
            return port  # A porta está disponível
        except socket.error as e:
            if attempt < max_attempts - 1:
                # O endereço está em uso, tentando a próxima porta
                port += 1
            else:
                raise Exception("Não foi possível encontrar uma porta disponível após várias tentativas.")

# Encontrando uma porta disponivel
port = find_available_port(host, port)

# Lista para armazenar os clientes conectados
clientes = []

# Dicionário para rastrear grupos de chats e clientes associados a cada grupo
chat_rooms = {}
# Função para tratar as mensagens dos clientes
def handle_client(client_socket):
    current_room = None  # Variável para rastrear o grupo de chat atual do cliente
    while True:
        try:
            # Recebe a mensagem do cliente
            data = client_socket.recv(1024)
            if not data:
                # Se não houver dados, o cliente desconectou
                print(f'Cliente {client_socket.getpeername()} desconectado.')
                if current_room:
                    chat_rooms[current_room].remove(client_socket)
                clientes.remove(client_socket)
                client_socket.close()
                break

            # Verifica se a mensagem é um comando
            message = data.decode('utf-8')
            if message.startswith('/criar'):
                _, room_name = message.split(' ', 1)
                room_name = room_name.strip()
                if create_chat_room(client_socket, room_name):
                    print(f'Grupo de chat "{room_name}" criado por {client_socket.getpeername()}')
                    current_room = room_name
                else:
                    print(f'Grupo de chat "{room_name}" já existe.')

            elif message.startswith('/listar'):
                list_chat_rooms(client_socket)

            elif message.startswith('/conectar'):
                _, room_name = message.split(' ', 1)
                room_name = room_name.strip()
                if room_name in chat_rooms:
                    if current_room:
                        chat_rooms[current_room].remove(client_socket)
                    chat_rooms[room_name].append(client_socket)
                    current_room = room_name
                    client_socket.send(f'Você está conectado ao chat "{room_name}"'.encode('utf-8'))
                else:
                    client_socket.send(f'Chat "{room_name}" não encontrado.'.encode('utf-8'))

            else:
                # Envie a mensagem recebida para todos os clientes no mesmo grupo de chat
                if current_room:
                    for client in chat_rooms.get(current_room, []):
                        client.send(data)
        except Exception as e:
            print(f'Erro na comunicação com o cliente {client_socket.getpeername()}: {e}')
            if current_room:
                chat_rooms[current_room].remove(client_socket)
            clientes.remove(client_socket)
            client_socket.close()
            break

# Função para criar um novo grupo de chat
def create_chat_room(client_socket, room_name):
    if room_name not in chat_rooms:
        chat_rooms[room_name] = [client_socket]
        return True
    else:
        return False

# Função para listar os chats disponíveis
def list_chat_rooms(client_socket):
    available_rooms = list(chat_rooms.keys())
    if available_rooms:
        client_socket.send(f'Chats disponíveis: {", ".join(available_rooms)}'.encode('utf-8'))
    else:
        client_socket.send('Nenhum chat disponível.'.encode('utf-8'))

# Configuração do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)
print(f'Servidor ouvindo em {host}:{port}')

# Loop principal para aceitar conexões de clientes
while True:
    try:
        # Aceita a conexão do cliente
        client_socket, client_addr = server.accept()
        print(f'Nova conexão de {client_addr}')
        
        # Adiciona o cliente à lista de clientes
        clientes.append(client_socket)
        
        # Inicia uma thread para tratar as mensagens do cliente
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
    except KeyboardInterrupt:
        print('Servidor encerrado.')
        break
    except Exception as e:
        print(f'Erro ao aceitar a conexão: {e}')

# Fecha o servidor
server.close()

