# Author: Jamie Caesar
# Twitter: @j_cae
# 
# This is a base script to be used as a starting point for more useful features.
# This script simply accepts an IP as an argument, prompts for the username
# and password of the device, and then attempts to capture the output of
# the configured "show" command.
#
# This script can be added upon to parse the returned data to give a more 
# useful output

import sys
import requests
import json
from getpass import getpass


def get_show_cmd(command, ip, user, password):
    '''
    This function makes the NXAPI call to retieve the output for the supplied
    command, using the supplied IP address and supplied credentials.  It returns
    the body of the response as long as a "success" code is returned.
    '''
    url='http://' + ip + '/ins'
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
    try:
        response = requests.post(url,data=json.dumps(payload), headers=myheaders,
            auth=(user,password)).json()
        status = response['ins_api']['outputs']['output']
        if status['code'] == '200':
            return response['ins_api']['outputs']['output']['body']
        else:
            print 'UNSUCCESSFUL Reponse\nReturn code: {}.  Message: {}\nInput Command: {}\
                '.format(status['code'], status['msg'], command)
    except ValueError:
        print 'Did not receive a response.\nPlease check the IP and credentials and try again.'
        print 'Also verify that "feature nxapi" has been enabled on the device.\n'
        sys.exit(0)
    


def main():
    # TODO: Set up Argparse to take in IP address as a script prompt.
    
    """
    Modify these please
    """
    mgmt_ip = '192.168.199.51'
    print "Connecting to " + mgmt_ip
    switchuser=raw_input('Username: ')
    switchpassword=getpass('Password: ')
    print "-------"

    data = get_show_cmd('show cdp neighbor', mgmt_ip, switchuser, switchpassword)
    print json.dumps(data, indent=2, separators=(',', ': '))


if __name__ == '__main__':
    main()