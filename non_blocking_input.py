import sys
import termios
import threading
import tty

from multiprocessing import Queue


class NonBlockingInput:
    def __init__(self):
        """
        Non blocking input. Spawns a thread to handle input from stdin.
        q to quit.
        """
        self.buffer = Queue()
        self.thread = threading.Thread(target=self._get_input, args=(self.buffer,))
        print('Starting input thread, q to quit.')
        print('Type g to increase fitness, b to decrease it')
        self.thread.start()

    def _get_input(self, buffer):
        """
        Internal method. Gets input on the thread and queues it.
        :type buffer: Queue
        """
        while True:
            _input = self.getchar()
            buffer.put(_input)
            if _input == 'q':
                print('Stopping input thread...')
                exit()

    def get(self):
        """
        Get input from the queue (non-blocking)
        :return: a char if there is one, None otherwise
        """
        if self.buffer.empty():
            return None
        return self.buffer.get(block=False)

    def available(self):
        """
        Return true if data is available
        :return: the char
        """
        return not self.buffer.empty()

    def input(self, text=None):
        """
        Behaves like the traditional input function, gets input
        and returns. Blocking until the user inputs. Doesn't require a return
        key press, just reads one char.
        :param text: Prompt text
        :return: the char
        """
        if text:
            self.put(text)
        return self.get()

    @staticmethod
    def put(text):
        """
        Write to stdout.
        :param text: Text to write.
        :return: None.
        """
        sys.stdout.write('%s' % text)
        sys.stdout.flush()

    @staticmethod
    def getchar():
        """
        Gets chars from stdin without the return key.
        :return: None
        """
        def _getchar():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        return _getchar()
