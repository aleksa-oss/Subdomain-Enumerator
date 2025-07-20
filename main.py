import queue
import dns.resolver
import threading
import argparse
import signal
import sys
import time
import re
from colorama import Fore, Style, init

init()

stop_event = threading.Event()
result_counter = {'tried': 0, 'found': 0}
lock = threading.Lock()

def signal_handler(sig, frame):
	print(f"\n{Fore.RED}[!] Stopping...{Style.RESET_ALL}")
	stop_event.set()

signal.signal(signal.SIGINT, signal_handler)

def is_valid_domain(domain):
	regex = r"^(?!\-)(?:[a-zA-Z0-9\-]{1,63}\.)+[a-zA-Z]{2,}$"
	return re.match(regex, domain) is not None

def list_builder(location):
	q = queue.Queue()
	with open(location, "r") as file:
		for line in file:
			q.put(line.strip())
	return q

def scanner(host, sub_queue, output_path):
	resolver = dns.resolver.Resolver()
	resolver.timeout = 2
	resolver.lifetime = 2

	while not stop_event.is_set():
		try:
			prefix = sub_queue.get_nowait()
		except queue.Empty:
			break

		subdomain = f"{prefix}.{host}"
		try:
			res = resolver.resolve(subdomain, "A")
			with lock:
				result_counter['found'] += 1
			for r in res:
				print(f"{Fore.GREEN}[+] {subdomain} ==> {r.address}{Style.RESET_ALL}")
				if output_path:
					with open(output_path, "a") as f:
						f.write(f"{subdomain} ==> {r.address}\n")
		except:
			pass
		finally:
			with lock:
				result_counter['tried'] += 1
			sub_queue.task_done()

def main():
	parser = argparse.ArgumentParser(description="Multithreaded Subdomain Scanner")
	parser.add_argument("domain", help="Target domain")
	parser.add_argument("-w", "--wordlist", default="subdomains.txt", help="Path to wordlist")
	parser.add_argument("-t", "--threads", type=int, default=50, help="Number of threads")
	parser.add_argument("-o", "--output", help="Save output to file")
	args = parser.parse_args()

	if not is_valid_domain(args.domain):
		print("[-] Invalid domain")
		sys.exit(1)

	try:
		sub_queue = list_builder(args.wordlist)
	except FileNotFoundError:
		print("[-] Wordlist file not found")
		sys.exit(1)

	start_time = time.time()
	threads = []

	for _ in range(args.threads):
		t = threading.Thread(target=scanner, args=(args.domain, sub_queue, args.output), daemon=True)
		t.start()
		threads.append(t)

	while any(t.is_alive() for t in threads):
		try:
			time.sleep(0.1)
		except KeyboardInterrupt:
			signal_handler(None, None)
			break

	end_time = time.time()
	elapsed = end_time - start_time
	tried = result_counter['tried']
	found = result_counter['found']

	print(f"\n{Style.BRIGHT}[*] Scan Summary:{Style.RESET_ALL}")
	print(f"{Fore.GREEN}[*] Found: {found}{Style.RESET_ALL}")
	print(f"{Fore.YELLOW}[*] Tried: {tried}{Style.RESET_ALL}")
	print(f"{Fore.BLUE}[*] Time: {elapsed:.2f}s{Style.RESET_ALL}")
	print(f"{Fore.MAGENTA}[*] Speed: {tried/max(1,elapsed):.1f} req/s{Style.RESET_ALL}")

if __name__ == "__main__":
	main()
