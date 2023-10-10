#!/usr/bin/python3
import socket
import struct
import sys
import subprocess
import argparse

def subnet_to_ip_range(subnet, port_scan=False, start_port=1, end_port=1024, timeout=1):
    try:
        d, s, c = socket.inet_aton, struct, '!I'
        f = lambda n: s.pack(c, n)
        g = lambda n: socket.inet_ntoa(f(n))

        def h(n, b):
            t = 32 - int(b)
            u = s.unpack(c, d(n))[0]
            v = (u >> t) << t
            w = v | ((1 << t) - 1)
            return g(v), g(w), [g(x) for x in range(v, w + 1)]

        start, end, ips = h(*subnet.split('/'))

        print(f'Subnet: {subnet}')
        print(f'IP Range: {start} - {end}')
        print('All IPs:')

        for i in ips:
            status = "up" if ping(i) else "down"
            color = "\033[32m" if status == "up" else "\033[31m"
            print(f'{color}{i}  \033[0m')

        if port_scan:  
            print('Port Scan Results:')
            for i in ips:
                open_ports = scan_ports(i, range(start_port, end_port + 1), timeout)
                if open_ports:
                    print(f'{i}: Open Ports - {open_ports}')

    except (ValueError, IndexError, socket.error) as e:
        print(f"Error: {e}")
    except subprocess.CalledProcessError:
        print("Error: Unable to execute the 'ping' command.")
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        sys.exit(1)

def ping(ip):
    try:
        output = subprocess.check_output(['ping', '-c', '1', '-W', '1', ip])
        if "1 received" in output.decode('utf-8'):
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

def scan_ports(ip, ports, timeout):
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Subnet to IP Range Converter with Port Scan')
    parser.add_argument('subnet', type=str, help='The subnet to convert to an IP range (e.g., 192.168.1.0/24)')
    parser.add_argument('-p', '--port-scan', action='store_true', help='Perform a port scan on each IP address')
    parser.add_argument('--start-port', type=int, default=1, help='Start port for port scan (default: 1)')
    parser.add_argument('--end-port', type=int, default=1024, help='End port for port scan (default: 1024)')
    parser.add_argument('--timeout', type=int, default=1, help='Timeout for port scan in seconds (default: 1)')

    args = parser.parse_args()
    subnet_to_ip_range(args.subnet, args.port_scan, args.start_port, args.end_port, args.timeout)
