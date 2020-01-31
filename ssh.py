"""
Module for interactive execution on remote hosts via ssh2-python
Provides (read only for now) RawIOBase interface to enable readline() commands
Only minimally tested
"""

import threading
import time
import socket
import io
import logging
import select
import queue

import ssh2.error_codes
import ssh2.channel
from ssh2.session import Session

from config import *

__all__ = ['SSHThread']

class SSH2Reader(io.RawIOBase):
    BLKSIZE=512
    TIMEOUT=1.0
    # TODO make configurable

    def __init__(self, sock: socket.socket, session: ssh2.session.Session, channel: ssh2.channel.Channel, stderr: bool):
        """
        :param sock:
        :param session:
        :param channel:
        :param stderr:
        """
        self.sock = sock
        self.channel = channel
        self.session = session
        self.stderr = stderr
        return

    def wait(self):
        blocks = self.session.block_directions()
        readfds = [self.sock] if blocks & ssh2.session.LIBSSH2_SESSION_BLOCK_INBOUND else []
        writefds = [self.sock] if blocks & ssh2.session.LIBSSH2_SESSION_BLOCK_OUTBOUND else []
        ret =  select.select(readfds, writefds, (), self.TIMEOUT)
        return ret

    def read(self, size=-1):
        # TODO check for session errors during read
        if size == -1:
            return self.readall()

        # Read from socket. If it would block, wait until the socket selects()
        while 1:
            if self.stderr:
                s, d = self.channel.read_stderr(size)
            else:
                s, d = self.channel.read(size)
            if s == ssh2.error_codes.LIBSSH2_ERROR_EAGAIN:
                self.wait()
                continue
            else:
                break

        return d

    def readall(self):
        buf = []
        while 1:
            d = self.read(self.BLKSIZE)
            buf.append(d)
            if len(d) != self.BLKSIZE:
                break
        return b''.join(buf)

    def close(self):
        self.channel.close()

    def readinto(self, b):
        tmp = self.read(self.BLKSIZE)
        l = len(tmp)
        if not l:
            return None
        b[:l] = tmp
        return len(tmp)

    def readable(self):
        return True

    def seekable(self):
        return False

    def writable(self):
        return False

class SSHThread(threading.Thread):
    MAXQ = 1024*1024

    def __init__(self, conifg: SnifferConfig):
        super().__init__(name=self.__class__.name, daemon=True)
        self.log = logging.getLogger(self.__class__.__name__)
        self.config = conifg
        self.queue = queue.Queue(maxsize=self.MAXQ)
        return

    def run(self):
        self.log.info("Thread starting")
        config = self.config
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((config.host, config.port))

        session = Session()
        session.handshake(sock)
        session.userauth_password(config.username, config.password)
        channel = session.open_session()
        channel.shell()
        channel.pty('vt100')
        session.set_blocking(False)
        cio = io.BufferedReader(SSH2Reader(sock, session, channel, False))
        cioe = io.BufferedReader(SSH2Reader(sock, session, channel, True))
        # TODO error checking above

        # Execute setup
        for cmd in config.setup:
            logging.debug("Execute setup command: '%s'", cmd)
            channel.write(cmd + '\n')

        channel.write("echo XXX_COMPLETE_XXX\n")
        channel.write("echo XXX_COMPLETE_XXX >&2\n")

        # Read back commands until we get to XXX_COMPLETE_XXX
        # From both stderr, stdout, mainly for debugging
        while 1:
            line = cio.readline().decode().strip()
            if line == 'XXX_COMPLETE_XXX': break
            logging.debug("STDOUT: %s", line)

        while 1:
            line = cioe.readline().decode().strip()
            if line == 'XXX_COMPLETE_XXX': break
            logging.debug("STDERR: %s", line)

        # Execute tcpdump
        logging.debug("Execute tcpdump command: '%s'", config.tcpdump)
        channel.write(config.tcpdump + '\n')

        while 1:
            pkt = cio.readline()
            if len(pkt) == 0:
                time.sleep(1)
            # logging.debug(pkt)
            self.queue.put(pkt)

        self.log.info("Thread terminating")
        return

    def get(self, timeout):
        return self.queue.get(timeout=timeout)

