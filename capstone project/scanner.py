import sys
import socket
from datetime import datetime
import threading

# A lock to prevent print statements from different threads from mixing up
print_lock = threading.Lock()

def scan_port(target_ip, port, open_ports):
    """
    Scans a single port on the target IP.
    If the port is open, it prints the result and adds it to the open_ports list.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((target_ip, port))  # if 0, port is open
        
        if result == 0:
            # Use the lock to ensure this print statement is not interrupted by another thread
            with print_lock:
                print(f"Port {port} is open")
            open_ports.append(port)
            
        s.close()
    
    except socket.error as e:
        # It's generally better not to print errors for every single port
        # that fails, as this can be very noisy.
        # print(f"Socket error on port {port}: {e}")
        pass

def main():
    if len(sys.argv) == 2:
        target = sys.argv[1]
    else:
        print("Invalid number of arguments.")
        print("Usage: python scanner.py <target>")
        sys.exit(1)
        
    # Resolve the target hostname to an IP address
    try: 
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(f"Error: Unable to resolve hostname '{target}'")
        sys.exit(1)
        
    # Banner
    print("_" * 50)
    print(f"Scanning target: {target} ({target_ip})")
    print(f"Time started: {datetime.now()}")
    print("_" * 50)

    # A shared list to store the open ports found by threads
    open_ports_found = []
    threads = []
    
    # Multithreaded scanning of ports
    try:
        for port in range(1, 65536):
            # Pass the shared list to each thread
            thread = threading.Thread(target=scan_port, args=(target_ip, port, open_ports_found))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete their execution
        for thread in threads:
            thread.join()
            
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected! Exiting program.")
        sys.exit(0)
    
    except socket.error as e :
        print(f"Socket error: {e}")
        sys.exit(1)

    # --- Final Report ---
    print("\n" + "_" * 50)
    print("Scan Complete.")
    if open_ports_found:
        print(f"Discovered {len(open_ports_found)} open port(s):")
        # Sort the list for clean output
        open_ports_found.sort()
        print(open_ports_found)
    else:
        print("No open ports were found.")
    print("_" * 50)

if __name__ == "__main__":
    main()