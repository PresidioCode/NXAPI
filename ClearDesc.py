from argparse import ArgumentParser
from nxapi_base import NXOS

def main(args):
    device = NXOS(args.mgmt_ip)
    device.PromptCreds()
    intfstatus = device.cli_show('show interface status')
    intflist = intfstatus['TABLE_interface']['ROW_interface']
    commands = []
    for intf in intflist:
        commands.append("int {} ;no description".format(intf['interface']))
    device.cli_conf(commands)
    print "Descriptions Cleared."

if __name__ == '__main__':
    parser = ArgumentParser(description = "Enter the IP address of the device to connect with.")
    parser.add_argument("mgmt_ip", help="The management IP address of the NXAPI device you are "
        "connecting to.")
    args = parser.parse_args()
    main(args)