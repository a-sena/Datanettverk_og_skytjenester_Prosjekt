import argparse
import socket
import time
import re
import threading
def parse_arguments():
    parser = argparse.ArgumentParser(description='Simpleperf')

 

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-s', '--server', action='store_true', help='Enable server mode')
    mode.add_argument('-c', '--client', action='store_true', help='Enable client mode')
    parser.add_argument('-I', '--server_ip', type=str, default='127.0.0.1', help='IP address of the simpleperf server')
    parser.add_argument('-b', '--bind', type=str, default='127.0.0.1', help='IP address of the server\'s interface where the client should connect, default=127.0.0.1')
    parser.add_argument('-p', '--server_port', type=int, default=8088, help='Port number on which the server should listen; the port must be an integer and in the range [1024,65535], default=8088')
    parser.add_argument('-t', '--total_time', type=int, default=25, help='The total duration in seconds for which data should be generated, default=25')
    parser.add_argument('-f', '--format', type=str, default='MB', choices=['B', 'KB', 'MB'], help='Choose the format of the summary of results - it should be either in B, KB or MB, default=MB')
    parser.add_argument('-i', '--interval', type=int, help='Print statistics per specified interval in seconds', default=None)
    parser.add_argument('-P', '--parallel', type=int, default=1, choices=range(1, 6), help='Number of parallel connections')
    parser.add_argument("-n", "--num", dest="no_of_bytes", type=str, help="transfer edilecek veri boyutu", default=0)
   
    return parser.parse_args()
def handle_client(client_socket, client_address, args):
      # Receive data in chunks of 1000 bytes and calculate received_bytes
    amount_of_bytes_received = 0
    start_time = time.time()

    while True:
        data = client_socket.recv(1000)
        if not data:
            break

        if b'BYE'in data:
            break

        amount_of_bytes_received += len(data)
    end_time = time.time()
    total_duration = end_time - start_time  #elapsed_time=total duration

    if args.format == "B":
        transfer_size = amount_of_bytes_received
    elif args.format == "KB":
        transfer_size = amount_of_bytes_received / 1000
    else:
        transfer_size = amount_of_bytes_received / 1000000

    print(transfer_size)
    rate_server = (transfer_size * 8) / total_duration
    
    print("{:<25} {:<10} {:<15} {:<15}".format("ID", "Interval", "Received", "Rate"))
    print("{0}:{1:<15} 0.0 - {2:.1f}       {3:.0f} {4:<2}      {5:.2f} Mbps".format(client_address[0], client_address[1], total_duration, transfer_size, args.format, rate_server))

    client_socket.send(b"ACK: BYE")
    client_socket.close()


def server(args):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((args.bind, args.server_port))
    server_socket.listen(1)

    print("---------------------------------------------")
    print("A simpleperf server is listening on port {}".format(args.server_port))
    print("---------------------------------------------")

    while True:

        print("Waiting for a client to connect...")
        client_socket, client_address = server_socket.accept()

        print("---------------------------------------------")
        print("A simpleperf client with {}:{} is connected with {}:{}".format(client_address[0], client_address[1], args.bind, args.server_port))
        print("---------------------------------------------")
        
        
        
        # Handle client connection in a separate thread
        t = threading.Thread(target=handle_client, args=(client_socket, client_address, args))

        t.start()
       


def parse_size(val):
    match = re.match(r"([0-9]+)([a-z]+)", val, re.I)
    if not match:
        raise ValueError("Invalid size value: {}".format(val))
    size, unit = match.groups()
    size = int(size)
    if unit.upper() == "B":
        return size
    elif unit.upper() == "KB":
        return size * 1000
    elif unit.upper() == "MB":
        return size * 1000000
    else:
        raise ValueError("Invalid unit: {}".format(unit))

def client(args):
    def single_connection():
        nonlocal successful_connections

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((args.server_ip, args.server_port))

        print("---------------------------------------------")
        print("Simpleperf client connecting to server {}, port {}".format(args.server_ip, args.server_port))
        print("---------------------------------------------")
        
        start_time = time.time()

        amount_of_bytes_sent = 0
        print("-" * 55)
        print("{:<25} {:<10} {:15} {:<15}".format("ID", "Interval", "Transfer", "Bandwidth"))
        print("_" *60)
        if args.interval:
            interval_start_time = start_time
            interval_bytes_sent = 0
            for i in range(args.interval, args.total_time + args.interval, args.interval):
                while time.time() - interval_start_time < args.interval:
                    data = bytes(1000)
                    client_socket.sendall(data)
                    amount_of_bytes_sent += len(data)
                    interval_bytes_sent += len(data)
                duration = args.interval
                rate_client = (interval_bytes_sent * 8) / (duration * 1000000)
                print("{:<25} {:<10} {:<15} {:.2f} Mbps".format("{}:{}".format(args.server_ip, args.server_port), "{}-{}".format(i - args.interval, i), "{:.1f} MB".format(interval_bytes_sent / 1000000), rate_client))
                interval_bytes_sent = 0
                interval_start_time = time.time()
        else:
            while time.time() - start_time < args.total_time:
                data = bytes(1000)
                client_socket.sendall(data)
                amount_of_bytes_sent += len(data)

        client_socket.sendall(b'BYE')

        while True:
            response = client_socket.recv(1024)
            if response == b"ACK: BYE":
                break

        client_socket.close()

        total_time_elapsed = time.time() - start_time
        rate_client = amount_of_bytes_sent * 8 / (total_time_elapsed * 1000000)

        print("-" * 60)
        print("{:<25} {:<10} {:<15} {:.2f} Mbps".format("{}:{}".format(args.server_ip, args.server_port), "0-{}".format(args.total_time), "{:.1f} MB".format(amount_of_bytes_sent / 1000000), rate_client))

    threads = []

    for _ in range(args.parallel):
        thread = threading.Thread(target=single_connection)
        thread.start()
        threads.append(thread)
        time.sleep(1)
    successful_connections = 0
    for thread in threads:
        thread.join()
        successful_connections += 1
    if successful_connections == args.parallel:
        print("All connections have completed successfully.")


if __name__ == '__main__':
    args = parse_arguments()
    if args.server:
        server(args)
    elif args.client:
        client(args)
