import json
import socket


HOSTTOSEND = 'localhost'
PORT_ROUTER = 5008
PORT_SERVER = 5007
PORT_CLIENTE = 5006
HOST_CLIENTE = '172.20.10.7'
HOST_ROUTER = '172.20.10.7'
HOST_SERVER = '172.20.10.7'
K = 8


def checkReceiverChecksum(receivedMessage, k, checksum):
    c1 = receivedMessage[0:k]
    c2 = receivedMessage[k:2 * k]
    c3 = receivedMessage[2 * k:3 * k]
    c4 = receivedMessage[3 * k:4 * k]

    if c1:
        c1 = int(c1, 2)
    else:
        c1 = 0

    if c2:
        c2 = int(c2, 2)
    else:
        c2 = 0

    if c3:
        c3 = int(c3, 2)
    else:
        c3 = 0

    if c4:
        c4 = int(c4, 2)
    else:
        c4 = 0

    receiver_sum = bin(c1 + c2 + int(checksum, 2) + c3 + c4 + int(checksum, 2))[2:]

    if (len(receiver_sum) > k):
        x = len(receiver_sum) - k
        receiver_sum = bin(int(receiver_sum[0:x], 2) + int(receiver_sum[x:], 2))[2:]

    ReceiverChecksum = ''
    for i in receiver_sum:
        if (i == '1'):
            ReceiverChecksum += '0'
        else:
            ReceiverChecksum += '1'

    finalsum = bin(int(checksum, 2) + int(ReceiverChecksum, 2))[2:]
    finalcomp = ''
    for i in finalsum:
        if (i == '1'):
            finalcomp += '0'
        else:
            finalcomp += '1'
    if (int(finalcomp, 2) == 0):
        return True
    else:
        return False


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', PORT_SERVER))

    sequence = 0

    while True:
        print('Esperando mensagens')
        data, adress = s.recvfrom(1024)
        if data:
            print(data)
            data = json.loads(data)
            msg = data["msg"]
            checksum = data["checksum"]
            sequence_received = data["sequence"]
            binary_converted = ' '.join(format(c, 'b') for c in bytearray(msg, "utf-8"))
            checksum_is_correct = checkReceiverChecksum(binary_converted, K, checksum)
            msg = msg.replace("|", " ")
            print("Mensagem recebida: " + msg)
            if sequence == sequence_received and checksum_is_correct:
                data_to_send = dict(msg=str(sequence), porta_origem=PORT_SERVER, porta_destino=PORT_CLIENTE, host_origem=HOST_SERVER, host_destino=HOST_CLIENTE)
                sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print("enviando reconhecimento para cliente: " + str(sequence))
                sok.sendto(bytes(json.dumps(data_to_send), "UTF-8"), (HOST_ROUTER, PORT_ROUTER))
                sequence = 0 if sequence_received == 1 else 1
            else:
                data_to_send = dict(msg=str(0 if sequence == 1 else 1), porta_origem=PORT_SERVER, porta_destino=PORT_CLIENTE, host_origem=HOST_SERVER, host_destino=HOST_CLIENTE)
                if sequence != sequence_received:
                    print("Pacote duplicado!")
                if not checksum_is_correct:
                    print("Erro no checksum recebido!")
                sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print("enviando reconhecimento para cliente: " + str(sequence))
                sok.sendto(bytes(json.dumps(data_to_send), "UTF-8"), (HOST_ROUTER, PORT_ROUTER))





