# Author: Jamie Caesar
# Twitter: @j_cae
# 
# 
# This file is meant to be a module of basic NXAPI operations that other
# scripts can leverage to push and pull data from NXAPI enabled devices.
#
#

import sys
import requests
import json
from getpass import getpass
from ipaddress import ip_address

class nxosDevice():
    _username = None
    _password = None
    _IP = None

    def __init__(self, IP):
        self._IP = ip_address(IP)

    def __repr__(self):
        return self._IP.exploded

    def __str__(self):
        return self__repr__()

    def getCredentials(self):
        print "Please supply credentials for device: {}".format(self.__repr__())
        if not self.setUsername():
            raise ValueError("Did not receive a valid username")
        else:
            if not self.setPassword():
                raise ValueError("Did not receive a valid password")

    def setPassword(self):
        value = getpass('Password: ')
        if len(value) > 0:
            self._password = value
            return True
        else:
            return False

    def setUsername(self):
        user = raw_input('Username: ')
        if len(user) > 0:
            self.username = user
            return True
        else:
            return False

    @property
    def username(self):
        return self._username
    
    @property
    def password(self):
        return self._password

    @property
    def ip(self):
        return self.__repr__()


def short_int(str):
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


def show_cmd(command, device):
    '''
    This function makes the NXAPI call to retieve the output for the supplied
    command, using the supplied IP address and supplied credentials.  It returns
    the body of the response as long as a "success" code is returned.
    '''
    url='http://' + device.ip + '/ins'
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
    response = requests.post(url,data=json.dumps(payload), headers=myheaders,
        auth=(device.username,device.password)).json()
    status = response['ins_api']['outputs']['output']
    if status['code'] == '200':
        return response['ins_api']['outputs']['output']['body']
    else:
        print 'UNSUCCESSFUL Reponse\nReturn code: {}.  Message: {}\nInput Command: {}\
            '.format(status['code'], status['msg'], command)
    

def conf_t(command_list, device):
    '''
    This function makes the NXAPI call to push the supplied list of commands
    using the supplied IP address and supplied credentials.
    '''
    sys.stdout.write("Writing commands")
    url='http://' + device.ip + '/ins'
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
    for command in command_list:
        payload["input"] = command
        response = requests.post(url,data=json.dumps(payload), headers=myheaders,
            auth=(device.username,device.password)).json()
        sys.stdout.write(".")
        # Verify Success
        resp_codes = response["ins_api"]["outputs"]["output"]
        if type(resp_codes) == dict:
            resp_codes = [resp_codes]
        for item in resp_codes:
            if item["code"] != '200':
                print "Command string {} had an error. Skipping.".format(command)
    sys.stdout.write("\n")
    return True


