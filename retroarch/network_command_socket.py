import socket

class NetworkCommandSocket(object):
  def __init__(port=55354, addr='127.0.0.1'):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.connect(addr, port)

  def read_core_ram(self, addr, size):
    msg = "READ_CORE_RAM %x %d\n" % (addr, size)
    self.socket.sendmsg(msg)
    msg, ancdata, flags, addr = self.socket.recvmsg(1024)
    # TODO: ignore ECONNREFUSED
