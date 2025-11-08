#!/usr/bin/env python3
import ipaddress
import shutil
from pathlib import Path

NUM_EDGES = 10
CORES = ["r1", "r2", "r3", "r4", "r5"]
CORE_AS = 65000

def assign_core(edge_id):
    return CORES[(edge_id - 1) % len(CORES)]

def edge_asn(edge_id):
    return 65100 + edge_id  # 65101.. up

def edge_loopback(edge_id):
    # Map 1..N into 100.64.x.y
    a = 100
    b = 64
    c = edge_id // 256
    d = edge_id % 256
    return f"{a}.{b}.{c}.{d}"

def link_subnet(edge_id):
    # /30s sequentially from 10.1.0.0
    block_index = edge_id - 1
    base_int = int(ipaddress.IPv4Address("10.1.0.0"))
    ip = ipaddress.IPv4Address(base_int + block_index * 4)
    return ipaddress.ip_network(f"{ip}/30")

CORE_LOOPBACKS = {
    "r1": "10.255.1.1",
    "r2": "10.255.2.2",
    "r3": "10.255.3.3",
    "r4": "10.255.4.4",
    "r5": "10.255.5.5",
}

RRs = ["r1", "r2"]  # route reflectors

DAEMONS_CONTENT = """\
zebra=yes
bgpd=yes
staticd=no
ospfd=no
ospf6d=no
ripd=no
ripngd=no
isisd=no
pimd=no
ldpd=no
nhrpd=no
eigrpd=no
babeld=no
sharpd=no
pbrd=no
fabricd=no
vrrpd=no
pathd=no
bfdd=no
vtysh_enable=yes
"""

lab_dir = Path("lab_bgp")
if lab_dir.exists():
    shutil.rmtree(lab_dir)
lab_dir.mkdir()

# Per-node dirs
for core in CORES:
    (lab_dir / core).mkdir()
for edge_id in range(1, NUM_EDGES + 1):
    (lab_dir / f"edge{edge_id:03d}").mkdir()

# Which edges connect to which core
core_eth_map = {c: [] for c in CORES}
for edge_id in range(1, NUM_EDGES + 1):
    core = assign_core(edge_id)
    core_eth_map[core].append(f"edge{edge_id:03d}")

# ---------- Edge configs ----------
for edge_id in range(1, NUM_EDGES + 1):
    edge_name = f"edge{edge_id:03d}"
    asn = edge_asn(edge_id)
    loop_ip = edge_loopback(edge_id)
    core = assign_core(edge_id)
    net = link_subnet(edge_id)
    hosts = list(net.hosts())
    core_ip = str(hosts[0])
    edge_ip = str(hosts[1])

    # frr.conf
    lines = [
        "frr defaults traditional",
        f"hostname {edge_name}",
        "service integrated-vtysh-config",
        "!",
        "log stdout",
        "!",
        "interface lo",
        f" ip address {loop_ip}/32",
        "!",
        "interface eth1",
        f" ip address {edge_ip}/{net.prefixlen}",
        "!",
        f"router bgp {asn}",
        f" bgp router-id {loop_ip}",
        " bgp log-neighbor-changes",
        " timers bgp 1 3",
        f" neighbor {core_ip} remote-as {CORE_AS}",
        " !",
        " address-family ipv4 unicast",
        f"  network {loop_ip}/32",
        f"  neighbor {core_ip} activate",
        " exit-address-family",
        "!",
        "line vty",
        " exec-timeout 0 0",
        "!",
    ]
    (lab_dir / edge_name / "frr.conf").write_text("\n".join(lines) + "\n")

    # daemons
    (lab_dir / edge_name / "daemons").write_text(DAEMONS_CONTENT)

# ---------- Core configs ----------
for core in CORES:
    lo_ip = CORE_LOOPBACKS[core]
    rr_mode = core in RRs

    lines = [
        "frr defaults traditional",
        f"hostname {core}",
        "service integrated-vtysh-config",
        "!",
        "log stdout",
        "!",
        "interface lo",
        f" ip address {lo_ip}/32",
        "!",
    ]

    # Edge-facing interfaces
    ethnum = 1
    for edge in core_eth_map[core]:
        edge_id = int(edge.replace("edge", ""))
        net = link_subnet(edge_id)
        hosts = list(net.hosts())
        core_ip = str(hosts[0])
        lines += [
            f"interface eth{ethnum}",
            f" ip address {core_ip}/{net.prefixlen}",
            "!",
        ]
        ethnum += 1

    # BGP
    lines += [
        f"router bgp {CORE_AS}",
        f" bgp router-id {lo_ip}",
        " bgp log-neighbor-changes",
        " timers bgp 1 3",
        " !",
        " neighbor CORE-PEERS peer-group",
        f" neighbor CORE-PEERS remote-as {CORE_AS}",
        " neighbor CORE-PEERS update-source lo",
    ]
    if rr_mode:
        lines.append(" neighbor CORE-PEERS route-reflector-client")
    lines.append(" !")

    # iBGP core neighbors
    for other, other_lo in CORE_LOOPBACKS.items():
        if other == core:
            continue
        lines.append(f" neighbor {other_lo} peer-group CORE-PEERS")

    # eBGP edge neighbors
    for edge in core_eth_map[core]:
        edge_id = int(edge.replace("edge", ""))
        asn = edge_asn(edge_id)
        net = link_subnet(edge_id)
        hosts = list(net.hosts())
        core_ip = str(hosts[0])
        lines += [
            " !",
            f" neighbor {core_ip} remote-as {asn}",
        ]

    # Address-family
    lines += [
        " !",
        " address-family ipv4 unicast",
        "  neighbor CORE-PEERS activate",
    ]

    ethnum = 1
    for edge in core_eth_map[core]:
        edge_id = int(edge.replace("edge", ""))
        net = link_subnet(edge_id)
        hosts = list(net.hosts())
        core_ip = str(hosts[0])
        lines.append(f"  neighbor {core_ip} activate")
        ethnum += 1

    lines += [
        " exit-address-family",
        "!",
        "line vty",
        " exec-timeout 0 0",
        "!",
    ]

    (lab_dir / core / "frr.conf").write_text("\n".join(lines) + "\n")
    (lab_dir / core / "daemons").write_text(DAEMONS_CONTENT)

# ---------- Containerlab topology ----------
nodes_yaml = []
links_yaml = []

# Cores
for core in CORES:
    nodes_yaml += [
        f"    {core}:",
        "      kind: linux",
        "      image: frrouting/frr:latest",
        "      binds:",
        f"        - ./{core}/frr.conf:/etc/frr/frr.conf",
        f"        - ./{core}/daemons:/etc/frr/daemons",
        "      exec:",
        "        - sysctl -w net.ipv4.ip_forward=1",
    ]

# Edges
for edge_id in range(1, NUM_EDGES + 1):
    edge = f"edge{edge_id:03d}"
    nodes_yaml += [
        f"    {edge}:",
        "      kind: linux",
        "      image: frrouting/frr:latest",
        "      binds:",
        f"        - ./{edge}/frr.conf:/etc/frr/frr.conf",
        f"        - ./{edge}/daemons:/etc/frr/daemons",
        "      exec:",
        "        - sysctl -w net.ipv4.ip_forward=1",
    ]

# Links core:ethX <-> edge:eth1
for core in CORES:
    ethnum = 1
    for edge in core_eth_map[core]:
        links_yaml.append(
            f'    - endpoints: ["{core}:eth{ethnum}", "{edge}:eth1"]'
        )
        ethnum += 1

topology = [
    "name: bgp-scale-lab",
    "",
    "mgmt:",
    "  network: mgmt-net",
    "  ipv4-subnet: 172.31.0.0/16",
    "",
    "topology:",
    "  nodes:",
    *nodes_yaml,
    "  links:",
    *links_yaml,
]

(lab_dir / "lab.clab.yml").write_text("\n".join(topology) + "\n")

print("Done. Files in ./lab_bgp")
