Wireshark Initial Response

We can filter inbound/outbound traffic by first using nslookup on the given domain. This returns the below destination address which we can plug into the following query (in Wireshark)
(ip.addr == 170.64.166.99 && tcp.port == 70) || (ip.dst == 170.64.166.99 && tcp.port == 70) 

