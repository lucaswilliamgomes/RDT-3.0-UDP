import socket
import json

TIMEOUT = 20
PORT_ROUTER = 5008
PORT_SERVER = 5007
PORT_CLIENTE = 5006
HOST_CLIENTE = '172.20.10.7'
HOST_ROUTER = '172.20.10.9'
HOST_SERVER = '172.20.10.7'
K = 8


def findChecksum(sentMessage, k):
    c1 = sentMessage[0:k]
    c2 = sentMessage[k:2 * k]
    c3 = sentMessage[2 * k:3 * k]
    c4 = sentMessage[3 * k:4 * k]

    # Calculando em binario a soma dos pacotes
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

    sum = bin(c1 + c2 + c3 + c4)[2:]

    if (len(sum) > k):
        x = len(sum) - k
        sum = bin(int(sum[0:x], 2) + int(sum[x:], 2))[2:]
    if (len(sum) < k):
        sum = '0' * (k - len(sum)) + sum

    checksum = ''
    for i in sum:
        if (i == '1'):
            checksum += '0'
        else:
            checksum += '1'
    return checksum


def calc_timeout(estimated_rtt, sample_rtt, dev_rtt, alpha=0.1, beta=0.1):
    estimated_rtt = (1 - alpha) * estimated_rtt + alpha * sample_rtt
    dev_rtt = (1 - beta) * dev_rtt + beta * abs(sample_rtt - estimated_rtt)
    timeout_interval = estimated_rtt + 4 * dev_rtt
    return timeout_interval


if __name__ == "__main__":
    # endereço para o qual os dados vão ser enviados


    # cria um UDP/IP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mensagens = ["Oi",
                 "tudo ",
                 "bem",
                 "?"
                 ]
    sequence = 0

    for msg in mensagens:
        print("Enviando mensagem: " + msg)
        msg = msg.replace(" ", "|")
        binary_converted = ' '.join(format(c, 'b') for c in bytearray(msg, "utf-8"))
        checksum = findChecksum(binary_converted, K)
        print("Checksum: " + checksum)
        data = dict(msg=msg, checksum=checksum, sequence=sequence, porta_origem=PORT_CLIENTE, porta_destino=PORT_SERVER, host_origem=HOST_CLIENTE, host_destino=HOST_SERVER)
        s.sendto(bytes(json.dumps(data), "UTF-8"), (HOST_ROUTER, PORT_ROUTER))
        print("Dados enviados: " + str(data))
        # Esperando reconhecimento do servidor
        while True:
            try:
                socket_to_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                socket_to_receive.bind(('', PORT_CLIENTE))
                socket_to_receive.settimeout(TIMEOUT)
                response, address = socket_to_receive.recvfrom(1024)
                if response:
                    print('Resposta (Ack): ' + str(response))
                    response = json.loads(response)
                    sequence_received = int(response["msg"])
                    if sequence_received != sequence:
                        # reenvio da mensagem
                        print("Reenviado mensagem devido a erro no numero de sequencia!")
                        s.sendto(bytes(json.dumps(data), "UTF-8"), (HOST_ROUTER, PORT_ROUTER))
                    if sequence_received == sequence:
                        print("Enviando próxima mensagem!")
                        sequence = 0 if sequence_received == 1 else 1
                        break
            except socket.timeout as msg:
                print("Reenviado mensagem devido a estouro no temporizador!")
                s.sendto(bytes(json.dumps(data), "UTF-8"), (HOST_ROUTER, PORT_ROUTER))

    print('closing socket')
    s.close()
