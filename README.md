# Implementing MRI and Latency

## Introduction

The objective of this is to extend basic L3 forwarding with a
scaled-down version of In-Band Network Telemetry (INT), which we call
Multi-Hop Route Inspection (MRI). And finding the time it has waited 
inside the queue when there is a heavy flow in the network

MRI allows users to track the path and the length of queues that every
packet travels through.  To support this functionality, you will need
to write a P4 program that appends an ID and queue length to the
header stack of every packet.  At the destination, the sequence of
switch IDs correspond to the path, and each ID is followed by the
queue length of the port at switch. Switch_Delay tells us about whether 
burst of traffic are there in the network that passes thorugh the switch.


## Run the code

The directory with this README also contains a skeleton P4 program,
`latency.p4`, which initially implements L3 forwarding and calculate the 
time it was inside the switch.


1. In your shell, run:
   ```bash
   make
   ```
   This will:
   * compile `latency.p4`, and
   * start a Mininet instance with three switches (`s1`, `s2`, `s3`) configured
     in a triangle. There are 5 hosts. `h1` and `h11` are connected to `s1`.
     `h2` and `h22` are connected to `s2` and `h3` is connected to `s3`.
   * The hosts are assigned IPs of `10.0.1.1`, `10.0.2.2`, etc
     (`10.0.<Switchid>.<hostID>`).
   * The control plane programs the P4 tables in each switch based on
     `sx-runtime.json`

2. We want to send a low rate traffic from `h1` to `h2` and a high
   rate iperf traffic from `h11` to `h22`.  The link between `s1` and
   `s2` is common between the flows and is a bottleneck because we
   reduced its bandwidth to 512kbps in topology.json.  Therefore, if we
   capture packets at `h2`, we should see high queue size and high latecy for that
   link.

![Setup](setup.png)

3. You should now see a Mininet command prompt. Open four terminals
   for `h1`, `h11`, `h2`, `h22`, respectively:
   ```bash
   mininet> xterm h1 h11 h2 h22
   ```
3. In `h2`'s xterm, start the server that captures packets:
   ```bash
   ./receive.py
   ```
4. in `h22`'s xterm, start the iperf UDP server:
   ```bash
   iperf -s -u
   ```

5. In `h1`'s xterm, send one packet per second to `h2` using send.py
   say for 30 seconds:
   ```bash
   ./send.py 10.0.2.2 "P4 is cool" 30
   ```
   The message "P4 is cool" should be received in `h2`'s xterm,
6. In `h11`'s xterm, start iperf client sending for 15 seconds
   ```bash
   iperf -c 10.0.2.22 -t 15 -u
   ```
7. At `h2`, the MRI header has no hop info (`count=0`)
8. type `exit` to close each xterm window

You should see the message received at host `h2`.

### A note about the control plane

P4 programs define a packet-processing pipeline, but the rules
governing packet processing are inserted into the pipeline by the
control plane.  When a rule matches a packet, its action is invoked
with parameters supplied by the control plane as part of the rule.

In this exercise, the control plane logic has already been
implemented.  As part of bringing up the Mininet instance, the
`make` script will install packet-processing rules in the tables of
each switch. These are defined in the `sX-runtime.json` files, where
`X` corresponds to the switch number.


got a packet
###[ Ethernet ]### 
  dst       = 08:00:00:00:01:01
  src       = 08:00:00:00:01:00
  type      = IPv4
###[ IP ]### 
     version   = 4
     ihl       = 14
     tos       = 0x0
     len       = 65
     id        = 1
     flags     = 
     frag      = 0
     ttl       = 62
     proto     = udp
     chksum    = 0x5ca9
     src       = 10.0.2.2
     dst       = 10.0.1.1
     \options   \
      |###[ MRI ]### 
      |  copy_flag = 0
      |  optclass  = control
      |  option    = 31
      |  length    = 36
      |  count     = 2
      |  \swtraces  \
      |   |###[ SwitchTrace ]### 
      |   |  swid      = 1
      |   |  qdepth    = 0
      |   |  swlat     = 0
      |   |  padd      = 78708736
      |   |###[ SwitchTrace ]### 
      |   |  swid      = 2
      |   |  qdepth    = 54
      |   |  swlat     = 27
      |   |  padd      = 4131127296
###[ UDP ]### 
        sport     = 1234
        dport     = 4321
        len       = 9
        chksum    = 0x6026
###[ Raw ]### 
           load      = 's'

#### Cleaning up Mininet

In the latter two cases above, `make` may leave a Mininet instance
running in the background.  Use the following command to clean up
these instances:

```bash
make stop
```

## Relevant Documentation

The documentation for P4_16 and P4Runtime is available [here](https://p4.org/specs/)

All excercises in this repository use the v1model architecture, the documentation for which is available at:
1. The BMv2 Simple Switch target document accessible [here](https://github.com/p4lang/behavioral-model/blob/master/docs/simple_switch.md) talks mainly about the v1model architecture.
2. The include file `v1model.p4` has extensive comments and can be accessed [here](https://github.com/p4lang/p4c/blob/master/p4include/v1model.p4).