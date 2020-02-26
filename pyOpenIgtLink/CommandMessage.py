from pyOpenIgtLink import *

IGTL_COMMAND_HEADER_SIZE = 138
IGTL_COMMAND_NAME_SIZE = 128


class CommandMessage(MessageBase):
    """
            :ivar _commandId The command id (uint32)
            :ivar _commandName The command name
            :ivar _commandContent The command content
            :ivar _encoding The command encoding
            :ivar _length The command length
    """

    def __init__(self):
        MessageBase.__init__(self)

        # Setting std header
        self._messageType = "COMMAND"
        self._headerVersion = IGTL_HEADER_VERSION_2

        # setting command header parameters
        self._commandId = 0
        self._commandName = np.zeros([128], dtype=np.uint8)
        self._commandContent = ""
        self._encoding = 3
        self._length = 0

    def setCommandId(self, cmdId):
        """
        Sets the command id
        :param cmdId: The command id
        """
        self._commandId = int(cmdId)

    def getCommandId(self):
        """
        Gets the command id
        :return: The command id
        """
        return self._commandId

    def setCommandName(self, name):
        """
        Sets the command name
        :param name: The command name
        """
        char_list = [ord(i) for i in list(name)]
        self._commandName[0:len(name)] = char_list
        self._commandName[len(name)::] = 0

    def getCommandName(self):
        """
        Gets the command name
        :return: The command name
        """
        charNameList = [str(chr(i)) for i in self._commandName if i != 0]
        commandNameString = "".join(charNameList)

        return commandNameString

    def setCommandContent(self, content):
        """
        Sets the command content
        :param content: The command content
        """
        self._commandContent = str(content)

    def getCommandContent(self):
        """
        Gets the command content
        :return: The command content
        """
        return self._commandContent

    def setContentEncoding(self, encoding):
        """
        Sets the command encoding
        :param encoding: The command encoding
        """
        self._encoding = encoding

    def getContentEncoding(self, encoding):
        """
        Gets the command encoding
        :return encoding: The command encoding
        """
        return self._encoding

    def _packContent(self, endian = ">"):

        # set the command header
        binary_cmd = struct.pack(endian + 'H', self._encoding)
        binary_cmd += struct.pack(endian + 'I', self._length)
        binary_cmd += struct.pack(endian + 'I', self._commandId)

        binary_cmd += self._commandName.tostring()

        # set the command data
        b = bytearray()
        b.extend(self._commandContent.encode())
        binary_cmd += b

        self.body = binary_cmd
        self._bodySize = len(self.body)

    def _unpackContent(self,  endian = ">"):
        pass
        img_binary_header = self.body[0:IGTL_COMMAND_HEADER_SIZE - IGTL_COMMAND_NAME_SIZE]
        unpacked_header = struct.unpack(endian + 'HII', img_binary_header)

        self._encoding = unpacked_header[0]
        self._length = unpacked_header[1]
        self._commandId = unpacked_header[2]

        commandName = self.body[IGTL_COMMAND_HEADER_SIZE - IGTL_COMMAND_NAME_SIZE:IGTL_COMMAND_HEADER_SIZE]
        self._commandName = np.frombuffer(commandName, dtype=np.uint8)

