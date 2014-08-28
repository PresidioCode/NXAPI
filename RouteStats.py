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
from ipaddress import ip_address


def RouteStats(routetable, vrf="default", addrf="ipv4"):
    # TODO:  Need to update to handle multiple VRFs and address families
    nexthop_stats = {}
    current_vrf = routetable['TABLE_vrf']['ROW_vrf']
    current_addrf = current_vrf['TABLE_addrf']['ROW_addrf']
    routes = current_addrf['TABLE_prefix']['ROW_prefix']
    for route in routes:
        nexthop_list = route['TABLE_path']['ROW_path']
        if type(nexthop_list) == dict:      #Only one next-hop
            nexthop_list = [nexthop_list]
        for nexthop in nexthop_list:
            nh_addr = ip_address(nexthop['ipnexthop'])
            if nh_addr in nexthop_stats:
                nexthop_stats[nh_addr] += 1
            else:
                nexthop_stats[nh_addr] = 1
    return nexthop_stats


def main(args):
    n9k = NXOS(args.mgmt_ip)
    n9k.PromptCreds()
    print "Gathering data."
    route_data = n9k.cli_show('show ip route')
    stats = RouteStats(route_data)
    for hop in sorted(stats.keys()):
        print "NextHop: " + str(hop) + "\t\tNum Routes: " + str(stats[hop])


if __name__ == '__main__':
    parser = ArgumentParser(description = "Enter the IP address of the device to connect with.")
    parser.add_argument("mgmt_ip", help="The management IP address of the NXAPI device you are "
        "connecting to.")
    args = parser.parse_args()
    main(args)
