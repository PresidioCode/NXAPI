# Author: Jamie Caesar
# Twitter: @j_cae
# 
# 
# This is a module of basic classes and functions that can be used to
# simplify the creation of NXAPI scripts.
#
#

import requests
import json
from getpass import getpass
from ipaddress import ip_address

class NXOS():
    '''
    This is a class to encapsulate the information needed to connect to
    an NXOS device via NXAPI.  The object is instantiated with an IP
    address and has setter methods to set credentials.  This class also
    leverages the "py2-ipaddress" module to verify valid IP address inputs.  
    '''

    def __init__(self, IP = None):
        self.ip = IP
        self.username = None
        self.password = None

    def __repr__(self):
        return "NXOS Device @ " + self.ip

    def __str__(self):
        return self.ip

    @property
    def username(self):
        return self._username    
    @username.setter
    def username(self, value):
        self._username = value
    
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, value):
        self._password = value

    @property
    def ip(self):
        return self._ip
    @ip.setter
    def ip(self, value):
        if isinstance(value, unicode):
            self._ip = ip_address(ip)
        else:
            self._ip = ip_address(unicode(ip))


    def PromptCreds(self):
        print "Please supply credentials for device: {}".format(str(self))
        user = raw_input('Username: ')
        if len(user) > 0:
            self.username = user
        else:
            self.username = None
        self.PromptPassword()


    def PromptPassword(self):
        value = getpass('Password: ')
        if len(value) > 0:
            self.password =value
        else:
            self.password = None


    def cli_show_raw(self, command):
        url='http://' + self.ip + '/ins'
        myheaders={'content-type':'application/json'}
        payload={
          "ins_api": {
            "version": "1.0",
            "type": "cli_show",
            "chunk": "0",
            "sid": "1",
            "input": command,
            "output_format": "json"
          }
        }
        assert type(command) == str, "Input to cli_show must be a string."
        assert type(self.username) == str, "Device does not have a valid username."
        assert type(self.password) == str, "Device does not have a valid password."
        try:
            response = requests.post(url,data=json.dumps(payload), headers=myheaders,
                auth=(self.username, self.password), timeout=10).json()
            return response
        except ValueError:
            raise ValueError("Did not receive proper JSON response. Check credentials.")


    def cli_show(self, command):
        '''
        This function makes the NXAPI call to retieve the output for the supplied
        command, using the supplied IP address and supplied credentials.  It returns
        the body of the response as long as a "success" code is returned.
        '''
        raw = self.cli_show_raw(command)
        status = raw['ins_api']['outputs']['output']
        if status['code'] == '200':
            return status['body']
        else:
            raise ValueError(status)


    def cli_conf(self, command_list):
        '''
        This function makes the NXAPI call to push the supplied list of commands
        using the supplied IP address and supplied credentials.
        '''
        url='http://' + self.ip + '/ins'
        myheaders={'content-type':'application/json'}
        payload={
          "ins_api": {
            "version": "1.0",
            "type": "cli_conf",
            "chunk": "0",
            "sid": "1",
            "input": None,
            "output_format": "json"
          }
        }
        assert type(command_list) == list, "Input to cli_conf must be a list."
        assert type(self.username) == str, "Device does not have a valid username."
        assert type(self.password) == str, "Device does not have a valid password."

        for command in command_list:
            payload["input"] = command
            try:
                response = requests.post(url,data=json.dumps(payload), headers=myheaders,
                    auth=(self.username, self.password),timeout=10).json()
            except ValueError:
                raise ValueError("Did not receive proper JSON response. Check credentials.")
            # Verify Success
            resp_codes = response["ins_api"]["outputs"]["output"]
            if type(resp_codes) == dict:
                resp_codes = [resp_codes]
            for item in resp_codes:
                if item["code"] != '200':
                    raise ValueError("{}, Input: {}".format(item['msg'], command))
        #TODO:  Return result codes in a list for all commands entered.  Will require
        #       breaking apart commands separated by ";" and associating them with the
        #       proper result code.


    def cli_show_save_txt(self, command, filename):
        '''
        This function makes the NXAPI call to retieve the output for the supplied
        command, using the supplied IP address and supplied credentials.  It saves
        the body of the response in a formatted and human readable way.  The
        output is saved to the supplied filename.
        '''
        raw = self.cli_show_raw(command)
        with open(filename, 'wb') as output:
            output.write(json.dumps(raw, indent=2, separators=(',', ': ')))


def short_intf(str):
  ''' 
  This function shortens the interface name for easier reading 
  '''
  replace_pairs = [
  ('tengigabitethernet', 'T'),
  ('gigabitethernet', 'G'),
  ('fastethernet', 'F'),
  ('ethernet', 'e'),
  ('eth', 'e'),
  ('port-channel' , 'Po')
  ]
  lower_str = str.lower()
  for pair in replace_pairs:
    if pair[0] in lower_str:
        return lower_str.replace(pair[0], pair[1])
  else:
    return str


def short_name(name):
    ''' This function will remove any domain suffixes (.cisco.com) or serial numbers
    that show up in parenthesis after the hostname'''
    #TODO: Some devices give IP address instead of name.  Need to ignore IP format.
    #TODO: Some CatOS devices put hostname in (), instead of serial number.  Find a way
    #       to catch this when it happens.
    return name.split('.')[0].split('(')[0]


    



