from argparse import ArgumentParser
from nxapi_core import nxosDevice, conf_t

def main(args):
    n9k = nxosDevice(args.mgmt_ip)
    n9k.getCredentials()
    commands = ['int m0 ;no desc', 'int e1/1-48 ;no desc', 'int e2/1-12 ;no desc', 
    'int Po1 ;no desc']
    if conf_t(commands, n9k):
        print "Descriptions Cleared."

if __name__ == '__main__':
    parser = ArgumentParser(description = "Enter the IP address of the device to connect with.")
    parser.add_argument("mgmt_ip", help="The management IP address of the NXAPI device you are "
        "connecting to.")
    args = parser.parse_args()
    main(args)