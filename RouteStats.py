# Author: Jamie Caesar
# Twitter: @j_cae
# 
# This script polls the device for the route table and outputs
# some routing statistics, such as:
# 1) How many interfaces are on the device
# 2) List the unique next-hops are in the route-table, and how many
#    routes point to each.
# 3) 
#

from argparse import ArgumentParser
from nxapi_base import NXOS
from ipaddress import ip_address, ip_network
from requests import Timeout


def GetRouteStats(routetable, vrf="default", addrf="ipv4"):
    # TODO:  Need to update to handle multiple VRFs and address families
    nh_stats = {}
    connected_types = ['direct', 'local', 'hsrp', 'vrrp', 'glbp']
    current_vrf = routetable['TABLE_vrf']['ROW_vrf']
    current_addrf = current_vrf['TABLE_addrf']['ROW_addrf']
    routes = current_addrf['TABLE_prefix']['ROW_prefix']
    for prefix in routes:
        # TODO: Multiple subnets on interface will overwrite previous
        nexthop_list = prefix['TABLE_path']['ROW_path']
        if type(nexthop_list) == dict:      #Only one next-hop
            nexthop_list = [nexthop_list]
        for nexthop in nexthop_list:
            intf = nexthop['ifname']
            subnet = ip_network(prefix['ipprefix'])
            nh_addr = ip_address(nexthop['ipnexthop'])
            client = nexthop['clientname']
            if intf not in nh_stats:
                nh_stats[intf] = {}
            if client in connected_types:    
                if client == 'direct':
                    nh_stats[intf][client] = subnet
                else:
                    nh_stats[intf][client] = nh_addr
            else:
                if 'hops' in nh_stats[intf]:
                    if nh_addr in nh_stats[intf]['hops']:
                        if client in nh_stats[intf]['hops'][nh_addr]:
                            nh_stats[intf]['hops'][nh_addr][client] += 1
                        else:
                            nh_stats[intf]['hops'][nh_addr][client] = 1
                    else:
                        nh_stats[intf]['hops'][nh_addr] = {client : 1}
                else:
                    nh_stats[intf]['hops'] = {nh_addr : {client : 1}}
    return nh_stats


def PrintRouteStats(stats):
    print ('-'*30)
    for intf in sorted(stats.keys()):
        print "{} (IP: {}, Net: {}):".format(intf, stats[intf]['local'], 
            stats[intf]['direct'])
        if 'hops' in stats[intf].keys():
            for hop in stats[intf]['hops']:
                for client in stats[intf]['hops'][hop]:
                    print " " * 4 + "Nexthop: {}\tNum Routes: {} ({})".format(str(hop), 
                        stats[intf]['hops'][hop][client], client)


def main(args):
    n9k = NXOS(args.mgmt_ip)
    n9k.PromptCreds()
    print "Gathering data."
    try:
        route_data = n9k.cli_show('show ip route')
        stats = GetRouteStats(route_data)
        PrintRouteStats(stats)
    except Timeout, e:
        print e
    except ValueError, e:
        print e
    print ""
    
if __name__ == '__main__':
    parser = ArgumentParser(description = "Enter the IP address of the device to connect with.")
    parser.add_argument("mgmt_ip", help="The management IP address of the NXAPI device you are "
        "connecting to.")
    args = parser.parse_args()
    main(args)
