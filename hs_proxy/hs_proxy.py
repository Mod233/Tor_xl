#!/usr/bin/env  python

import socket
import select
import ConfigParser
import thread

configFile = 'proxy.conf'
BUFSIZ = 1024


def getLocalProxyInfo(configFile):
    cp  = ConfigParser.SafeConfigParser()
    cp.read(configFile)
    host = cp.get('local_proxy', 'host')
    port = cp.getint('local_proxy', 'port')
    return (host, port)


def getTargetInfo(configFile):
    cp  = ConfigParser.SafeConfigParser()
    cp.read(configFile)
    host = cp.get('target', 'host')
    port = cp.getint('target', 'port')
    return (host, port)


def relayTcpStream(socketA, socketB):
    inputList =  [socketA, socketB]
    try:
        while True:
            readyInput, readyOutput, readyException = select.select(inputList,[],[])
            for inSocket in readyInput:
                if inSocket == socketA:
                    data = socketA.recv(BUFSIZ)
                    if not data:
                        break
                    socketB.send(data)
                elif inSocket == socketB:
                    data = socketB.recv(BUFSIZ)
                    if not data:
                        break
                    socketA.send(data)
    except Exception, e:
        print 'connection closed'
        socketA.close()
        socketB.close()


def main():
    localAddr = getLocalProxyInfo(configFile)
    tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSerSock.bind(localAddr)
    tcpSerSock.listen(10)
    try:
        while True:
            print 'waiting for connection...'
            tcpCliSock, addr = tcpSerSock.accept()
            print '...connected from:', addr
            try:
                dstAddr = getTargetInfo(configFile)
                tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcpClient.connect(dstAddr)
            except Exception, e:
                print 'failed to connect to target'
                tcpClient.close()
                tcpCliSock.close()
            else:
                thread.start_new_thread(relayTcpStream, (tcpCliSock, tcpClient))
    except Exception, e:
        print 'unhandled error occours!'
        tcpSerSock.close()


if __name__ == '__main__':
    main()


