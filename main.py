import socket
import concurrent.futures
from tqdm import tqdm
from termcolor import colored

# ASCII Art
ascii_art = """
                  888             
                  888             
                  888             
 .d88b.  88888b.  888888 888  888 
d8P  Y8b 888 "88b 888    888  888 
88888888 888  888 888    888  888 
Y8b.     888  888 Y88b.  Y88b 888 
 "Y8888  888  888  "Y888  "Y88888 
                              888 
                         Y8b d88P 
                          "Y88P"  
"""

def scan_port(ip, port, timeout=0.5, check_service=False):
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            service_name = socket.getservbyport(port) if check_service else ""
            return port, True, service_name
    except (socket.timeout, ConnectionRefusedError):
        return port, False, None
    except socket.error as e:
        return port, None, str(e)

def scan_ports(target, start_port, end_port, num_threads=100, check_service=False):
    try:
        ip = socket.gethostbyname(target)
        print(f"Scanning ports for {target} ({ip})...\n")

        open_ports = []
        errors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(scan_port, ip, port, check_service=check_service) for port in range(start_port, end_port + 1)]

            for future in tqdm(concurrent.futures.as_completed(futures), total=end_port - start_port + 1):
                port, result, service_name = future.result()
                if result is True:
                    open_ports.append((port, service_name))
                elif result is None:
                    errors.append((port, str(service_name)))

        if open_ports:
            print("\nOpen ports:")
            for port, service_name in open_ports:
                print(f"Port {port}: Open ({service_name})")
        else:
            print("\nNo open ports found.")

        if errors:
            print("\nErrors occurred:")
            for port, error in errors:
                print(f"Port {port}: {error}")

    except socket.gaierror:
        print("Invalid target. Please provide a valid IP address or domain name.")
    except KeyboardInterrupt:
        print("\nScan interrupted.")

# Print ASCII art
print(colored(ascii_art, "magenta"))

# Prompt the user for input
try:
    target = input("Enter the target IP address or domain name: ")
except KeyboardInterrupt:
    print("\nInput interrupted.")
    exit()

range_option = input("Do you want to scan the entire port range (0 - 65535)? (Y/N): ").lower()

if range_option == "y":
    start_port = 0
    end_port = 65535
else:
    try:
        start_port = int(input("Enter the starting port number: "))
        end_port = int(input("Enter the ending port number: "))
    except ValueError:
        print("Invalid port number.")
        exit()

num_threads = int(input("Enter the number of threads to use (recommended: 100): "))
check_service = input("Do you want to check the associated service names? (Y/N): ").lower() == "y"

# Perform the port scan
scan_ports(target, start_port, end_port, num_threads, check_service)

# Wait for Enter key to close the application
input("\nPress Enter to exit...")
