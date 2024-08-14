#!/usr/bin/env python3
import sys
import csv
from scapy.all import (
    FieldLenField,
    IntField,
    IPOption,
    Packet,
    PacketListField,
    ShortField,
    get_if_list,
    sniff,
    IP, UDP
)
from scapy.layers.inet import _IPOption_HDR


def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

class SwitchTrace(Packet):
    fields_desc = [ IntField("swid", 0),
                  IntField("qdepth", 0),
                  IntField("swlat", 0),
                  IntField("padd", 0)]
    def extract_padding(self, p):
                return "", p

class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swtraces",
                                  adjust=lambda pkt,l:l*2+4),
                    ShortField("count", 0),
                    PacketListField("swtraces",
                                   [],
                                   SwitchTrace,
                                   count_from=lambda pkt:(pkt.count*1)) ]

def handle_pkt(pkt):
    def handle_pkt(pkt):
    with open("output.txt", "a") as f:
        f.write("got a packet\n")
        f.write(pkt.show2(dump=True))
        f.write("\n")
    sys.stdout.flush()
    # To generate a csv with the below property
    # data = []
    # if pkt.haslayer(IPOption_MRI):
    #     data.append(pkt[IP].src)
    #     data.append(pkt[IP].dst)
    #     data.append(pkt[UDP].sport)
    #     data.append(pkt[UDP].dport)
    #     data.append(pkt[IP].proto)
    #     for swtrace in pkt[IPOption_MRI].swtraces:
    #         data.append(swtrace.swlat)

    #     with open("packet_data.csv", "a", newline='') as csvfile:
    #         writer = csv.writer(csvfile)
    #         writer.writerow(data)

    # print("got a packet")
    # pkt.show2()
    # sys.stdout.flush()


def main():
    iface = 'eth0'
    print("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(filter="udp and port 4321", iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
