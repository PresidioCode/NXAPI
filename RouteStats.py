# Author: Jamie Caesar
# Twitter: @j_cae
# 
# This script polls the device for the route table and outputs
# some routing statistics, such as:
# 1) A list of interfaces on the device and associated IP
# 2) List of next-hops per interface and a count of routes of each 
#    protocol. 
#

from argparse import ArgumentParser
from nxapi_base import NXOS
from ipaddress import ip_address, ip_network
from requests import Timeout


def GetRouteStats(routetable, vrf="default", addrf="ipv4"):
    '''
    This function takes the route-table data structure via NXAPI and returns a
    new data structure that stores route stats on a per-interface basis.
    
    For each interface it returns:
    *  The IP of the interface (local route)
    *  The network route for the interface (direct route)
    *  FHRP interface IP (hspr, vrrp, glbp route)
    *  Each next-hop address out that interface (if any exist).  For each next-hop:
        * A count of routes for each routing protocol that uses that next-hop.
    '''
    # TODO:  Need to update to handle multiple VRFs and address families
    nh_stats = {}
    connected_types = ['direct', 'local', 'hsrp', 'vrrp_engine']
    current_vrf = routetable['TABLE_vrf']['ROW_vrf']
    current_addrf = current_vrf['TABLE_addrf']['ROW_addrf']
    routes = current_addrf['TABLE_prefix']['ROW_prefix']
    for prefix in routes:
        # TODO: FIX: Secondary IPs on interface will overwrite previous entry
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
    '''
    This fucntion takes the route statistics from the GetRouteStats() function
    and prints them to the screen with some formatting.
    '''
    print ('-'*30)
    for intf in sorted(stats.keys()):
        keys = stats[intf].keys()
        if 'hsrp' in keys:
            print "{} (IP: {}, Net: {} , HSRP: {}):".format(intf, stats[intf]['local'], 
                stats[intf]['direct'], str(stats[intf]['hsrp']))
        elif 'vrrp_engine' in keys:
            print "{} (IP: {}, Net: {} , VRRP: {}):".format(intf, stats[intf]['local'], 
                stats[intf]['direct'], str(stats[intf]['vrrp_engine']))
        else:       
            print "{} (IP: {}, Net: {}):".format(intf, stats[intf]['local'], 
            stats[intf]['direct'])
        if 'hops' in stats[intf].keys():
            for hop in stats[intf]['hops']:
                for client in stats[intf]['hops'][hop]:
                    print " " * 4 + "Nexthop: {}\tRoutes: {} ({})".format(str(hop), 
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
