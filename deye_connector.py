import socket
import logging

from deye_config import DeyeConfig


class DeyeConnector:

    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger(DeyeConnector.__name__)
        self.config = config.logger

    def send_request(self, req_frame):
        for res in socket.getaddrinfo(self.config.ip_address, self.config.port, socket.AF_INET, socket.SOCK_STREAM):
            family, socktype, proto, canonname, sockadress = res
            try:
                client_socket = socket.socket(family, socktype, proto)
                client_socket.settimeout(10)
                client_socket.connect(sockadress)
            except socket.error as msg:
                self.__log.warn("Could not open socket")
                break

            self.__log.debug("Request frame: %s", frame.hex())
            client_socket.sendall(req_frame)

            attempts = 5
            while (attempts > 0):
                attempts = attempts - 1
                try:
                    data = client_socket.recv(1024)
                    try:
                        data
                    except:
                        self.__log.warn("No data received")
                    self.__log.debug("Response frame: %s", data.hex())
                    return data
                except socket.timeout as msg:
                    self.__log.warn("Connection timeout")
                except Exception as e:
                    self.__log.warn("Connection error", e.message)

        return bytearray()
