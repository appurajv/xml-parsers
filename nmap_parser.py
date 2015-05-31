#!/usr/bin/env python
# Author: Chris Duffy
# Date: May 2015
# Purpose: An script that can process and parse NMAP XMLs
# Returnable Data: A dictionary of hosts{iterated number} = [[hostnames], address, protocol, port, service name]
# Name: nmap_parser.py

import sys
import xml.etree.ElementTree as etree
import argparse
import collections

try:
    import nmap_doc_generator as gen
except:
    sys.exit("[!] Please download the nmap_doc_generator.py script")
from StringIO import StringIO

class Nmap_parser:
    def __init__(self, nmap_xml, verbose=0):
        try:
            self.hosts = self.nmap_parser(nmap_xml, verbose)
        except Exception, e:
            print("[!] There was an error %s") % (str(e))
            sys.exit(1)

    def nmap_parser(self, nmap_xml, verbose):
        # Parse the nmap xml file and extract hosts and place them in a dictionary
        # Input: Nmap XML file and verbose flag
        # Return: Dictionary of hosts [iterated number] = [hostname, address, protocol, port, service name, state]
        if not nmap_xml:
            sys.exit("[!] Cannot open Nmap XML file: %s \n[-] Ensure that your are passing the correct file and format" % (nmap_xml))
        try:
            tree = etree.parse(nmap_xml)
        except:
            sys.exit("[!] Cannot open Nmap XML file: %s \n[-] Ensure that your are passing the correct file and format" % (nmap_xml))
        hosts={}
        services=[]
        hostname_list=[]
        root = tree.getroot()
        hostname_node = None
        if verbose > 0:
            print ("[*] Parsing the Nmap XML file: %s") % (nmap_xml)
        for host in root.iter('host'):
            hostname = "Unknown hostname"
            for addresses in host.iter('address'):
                hwaddress = "No MAC Address ID'd"
                ipv4 = "No IPv4 Address ID'd"
                addressv6 = "No IPv6 Address ID'd"
                temp = addresses.get('addrtype')
                if "mac" in temp:
                    hwaddress = addresses.get('addr')
                    if verbose > 2:
                        print("[*] The host was on the same broadcast domain")
                if "ipv4" in temp:
                    address = addresses.get('addr')
                    if verbose > 2:
                        print("[*] The host had an IPv4 address")
                if "ipv6" in temp:
                    addressv6 = addresses.get('addr')
                    if verbose > 2:
                        print("[*] The host had an IPv6 address")
            try:
                hostname_node = host.find('hostnames').find('hostname')
            except:
                if verbose > 1:
                    print ("[!] No hostname found")
            if hostname_node is not None:
                hostname = hostname_node.get('name')
            else:
                hostname = "Unknown hostname"
                if verbose > 1:
                    print("[*] The hosts hostname is %s") % (str(hostname_node))
            for item in host.iter('port'):
                state = item.find('state').get('state')
                #if state.lower() == 'open':
                hostname_list.append(hostname)
                service = item.find('service').get('name')
                protocol = item.get('protocol')
                port = item.get('portid')
                services.append([hostname_list, address, protocol, port, service, hwaddress, state])
                hostname_list=[]
        for i in range(0, len(services)):
            service = services[i]
            index = len(service) - 1
            hostname = str1 = ''.join(service[0])
            address = service[1]
            protocol = service[2]
            port = service[3]
            serv_name = service[4]
            hwaddress = service[5]
            state = service[6]
            hosts[i] = [hostname, address, protocol, port, serv_name, hwaddress, state]
            if verbose > 2:
                print ("[+] Adding %s with an IP of %s:%s with the service %s")%(hostname,address,port,serv_name)
        if hosts:
            if verbose > 4:
                print ("[*] Results from NMAP XML import: ")
                for key, entry in hosts.iteritems():
                    print("[*] %s") % (str(entry))
            if verbose > 0:
                print ("[+] Parsed and imported unique ports %s") % (str(i+1))
            return(hosts)
        else:
            if verbose > 0:
                print ("[-] No ports were discovered in the NMAP XML file")

    def hostsReturn(self):
        # A controlled return method
        # Input: None
        # Returned: The processed hosts
        try:
             return self.hosts
        except Exception as e:
            print("[!] There was an error returning the data %s") % (e)

if __name__ == '__main__':
    # If script is executed at the CLI
    usage = '''usage: %(prog)s [-x reports.xml] -q -v -vv -vvv'''
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("-x", "--xml", type=str, help="Generate a dictionary of data based on a NMAP XML import, more than one file may be passed, separated by a comma", action="store", dest="xml")
    parser.add_argument("-f", "--filename", type=str, action="store", dest="filename", help="The filename that will be used to create an XLSX")
    parser.add_argument("-v", action="count", dest="verbose", default=1, help="Verbosity level, defaults to one, this outputs each command and result")
    parser.add_argument("-q", action="store_const", dest="verbose", const=0, help="Sets the results to be quiet")
    parser.add_argument('--version', action='version', version='%(prog)s 0.43b')
    args = parser.parse_args()

    # Argument Validator
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    # Set Constructors
    xml = args.xml                      # nmap XML
    verbose = args.verbose              # Verbosity level
    xml_list=[]                         # List to hold XMLs

    # Set return holder
    hosts=[]                            # List to hold instances
    hosts_temp={}                       # Temporary dictionary, which holds returned data from specific instances
    hosts_dict={}                       # Dictionary, which holds the combined returned dictionaries
    processed_hosts={}                  # The dictionary, which holds the unique values from all processed XMLs
    count = 0                           # Count for combining dictionaries
    unique = set()

    if not filename:
        if os.name != "nt":
             filename = dir + "/nmap_output"
        else:
             filename = dir + "\\nmap_output"
    else:
        if filename:
            if "\\" or "/" in filename:
                if verbose > 1:
                    print("[*] Using filename: %s") % (filename)
        else:
            if os.name != "nt":
                filename = dir + "/" + filename
            else:
                filename = dir + "\\" + filename
                if verbose > 1:
                    print("[*] Using filename: %s") % (filename)

    # Instantiation for proof of concept
    if "," in xml:
        xml_list = xml.split(',')
    else:
        xml_list.append(xml)
    for x in xml_list:
        try:
            tree_temp = etree.parse(x)
        except:
            sys.exit("[!] Cannot open XML file: %s \n[-] Ensure that your are passing the correct file and format" % (x))
        try:
            root = tree_temp.getroot()
            name = root.get("scanner")
            if name is not None and "nmap" in name:
                if verbose > 1:
                    print ("[*] File being processed is an NMAP XML")
                hosts.append(Nmap_parser(x, verbose))
            else:
                print("[!] File % is not an NMAP XML") % (str(x))
                sys.exit(1)
        except Exception, e:
            print("[!] Processing of file %s failed %s") % (str(x), str(e))
            sys.exit(1)

    # Processing of each instance returned to create a composite dictionary
    if not hosts:
        sys.exit("[!] There was an issue processing the data")
    for inst in hosts:
        hosts_temp = inst.hostsReturn()
        if hosts_temp is not None:
            for k, v in hosts_temp.iteritems():
                hosts_dict[count] = v
                count+=1
            hosts_temp.clear()
    if verbose > 3:
        for key, value in hosts_dict.iteritems():
            print("[*] Key: %s Value: %s") % (key,value)
    temp = [(k, hosts_dict[k]) for k in hosts_dict]
    temp.sort()
    for k, v in temp:
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        if str(v) in str(processed_hosts.values()):
            continue
        processed_hosts[k] = v

    # Generator for XLSX documents
    gen.docGenerator(verbose, hosts_dict, filename)

    # Printout of dictionary values
    #if verbose > 0:
    #    for key, target in processed_hosts.iteritems():
    #        print "[*] Hostname: %s IP: %s Protocol: %s Port: %s Service: %s State: %s MAC address: %s" % (target[0],target[1],target[2],target[3],target[4],target[6],target[5])
