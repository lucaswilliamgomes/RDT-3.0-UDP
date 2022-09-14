import socket
import json
import time

PORT_ROUTER = 5008
#HOST = 'localhost'
HOST_ROUTER = '10.94.15.221'
HOST_CLIENTE = '10.94.15.220'

print(socket.gethostbyname(socket.gethostname()))

def corromperPacote(data):
    if "checksum" in data:
        checksum = data["checksum"]
        if checksum:
            checksum = list(checksum)
            checksum[0] = '1' if checksum[0] == '0' else '0'
            data['checksum'] = ''.join(checksum)
    return data


def perdaDePacote():
    time.sleep(20.1)


def perdaDeAck(data):
    if "porta_origem" == 5007 in data:
        time.sleep(20.1)


def corrompeSequence(data):
    print(data)
    if "sequence" in data:
        sequence = int(data["sequence"])
        if sequence == 0:
            sequence = 1
            data["sequence"] = sequence
        else:
            sequence = 0
            data["sequence"] = sequence

    print(data)
    return data


def menuIntercepcoes(data, case):
    if case == 1:  # manda pacote normal
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (host_destino, port_destino))

    elif case == 2:  # mandar ckecksum corrompido
        data = corromperPacote(json.loads(data))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(json.dumps(data), "UTF-8"), (host_destino, port_destino))

    elif case == 3: #perde o pacote
        perdaDePacote()
        return

    elif case == 4: #perde o ack
        perdaDeAck(data)

    elif case == 5: #corrompe bit de sequencia
        data = corrompeSequence(json.loads(data))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(json.dumps(data), "UTF-8"), (host_destino, port_destino))

    else:
        print('Opção inválida!')
        return


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", PORT_ROUTER))

if __name__ == "__main__":
    while True:
        print('Esperando dados')
        data, address = s.recvfrom(1024)
        if data:
            print("Dados recebidos: " + str(data))
            port_destino = json.loads(data)["porta_destino"]
            host_destino = json.loads(data)["host_destino"]
            print("Como você deseja entregar os dados?: ")
            print("1-Sem modificações "
                  "2-Checksum corrompido "
                  "3-Perda de pacote "
                  "4-Perda do Ack "
                  "5-Corrompe Sequencia "
                  "6-Timeout prematuro")
            case = int(input('Opção escolhida: '))
            menuIntercepcoes(data, case)
