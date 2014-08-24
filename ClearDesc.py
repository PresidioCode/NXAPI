from argparse import ArgumentParser
from nxapi_base import NXOS

def main(args):
    n9k = NXOS(args.mgmt_ip)
    n9k.PromptCreds()
    commands = ['int m0 ;no desc', 'int e1/1-48 ;no desc', 'int e2/1-12 ;no desc', 
    'int Po1 ;no desc']
    n9k.cli_conf(commands)
    print "Descriptions Cleared."

if __name__ == '__main__':
    parser = ArgumentParser(description = "Enter the IP address of the device to connect with.")
    parser.add_argument("mgmt_ip", help="The management IP address of the NXAPI device you are "
        "connecting to.")
    args = parser.parse_args()
    main(args)