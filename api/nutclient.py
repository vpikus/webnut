import logging
import nutsock

class NutClientCmdError(Exception):
    """NUT (Network UPS Tools) client exception."""

class NutClient:
    """NUT (Network UPS Tools) client."""

    def __init__(self, host="127.0.0.1", port=3493, timeout=5):
        """
        Class initialization method.

        Parameters:
        - host (str): The hostname or IP address of the NUT server.
        - port (int): The port number of the NUT server.
        - timeout (int): The timeout in seconds for the socket connection.
        """
        logging.debug("NutClient initialization")
        logging.debug(f"    Host: {host}, Port: {port}")
        self.host = host
        self.port = port
        self.timeout = timeout

    def list_ups(self):
        """
        List the UPSes on the NUT server.

        Returns:
        - ups_dict: A dictionary of UPS names and descriptions.
        """
        with nutsock.NutSock(self.host, self.port, self.timeout) as sock:
            sock.connect()
            command = "LIST UPS"
            sock.cmd(command)
            raw_result = sock.read_until("\n")
            if raw_result != "BEGIN LIST UPS\n":
                raise NutClientCmdError(f"Invalid response from '{command}' comand: {raw_result}")
            raw_result = sock.read_until("END LIST UPS\n")
        
        ups_dict = {}
        for line in raw_result.split("\n"):
            if line.startswith("UPS "):
                _, name, description = line.split(" ", 2)
                description = description.strip('"')
                ups_dict[name] = description
        return ups_dict

    def list_vars(self, upsname):
        """
        List the variables for a UPS on the NUT server.

        Parameters:
        - upsname (str): The name of the UPS.

        Returns:
        - str: The response from the NUT server.
        """
        with nutsock.NutSock(self.host, self.port, self.timeout) as sock:
            sock.connect()
            command = f"LIST VAR {upsname}"
            sock.cmd(command)
            raw_result = sock.read_until("\n")
            if raw_result != f"BEGIN LIST VAR {upsname}\n":
                raise NutClientCmdError(f"Invalid response from '{command}' comand: {raw_result}")
            raw_result = sock.read_until(f"END LIST VAR {upsname}\n")
        
        vars_dict = {}
        for line in raw_result.split("\n"):
            if line.startswith("VAR "):
                _, _, var, value = line.split(" ", 3)
                vars_dict[var] = value.strip('"').strip()
        return vars_dict
    
    def get_var(self, upsname, var):
        """
        Get the value of a variable for a UPS on the NUT server.

        Parameters:
        - upsname (str): The name of the UPS.
        - var (str): The name of the variable.

        Returns:
        - str: The value of the variable.
        """
        with nutsock.NutSock(self.host, self.port, self.timeout) as sock:
            sock.connect()
            command = f"GET VAR {upsname} {var}"
            sock.cmd(command)
            raw_result = sock.read_until("\n")
            if not raw_result.startswith(f"VAR {upsname} {var} "):
                raise NutClientCmdError(f"Invalid response from '{command}' comand: {raw_result}")
        
        try:
            value = raw_result.split('"')[1]
            return value
        except IndexError:
            raise NutClientCmdError(f"Invalid response from '{command}' comand: {raw_result}")    
        

