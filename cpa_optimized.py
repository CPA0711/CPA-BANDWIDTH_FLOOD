#!/usr/bin/env python3
"""
BANDWIDTH OPTIMIZED TESTER 
"""

import socket
import ssl
import threading
import time
import sys
from urllib.parse import urlparse
from colorama import init, Fore, Style

init(autoreset=True)

class OptimizedTester:
    def __init__(self):
        self.results = []
    
    def test_single(self, url, threads=5, duration=10):
        """Test dengan konfigurasi optimasi"""
        parsed = urlparse(url)
        target = parsed.hostname
        use_https = parsed.scheme == 'https'
        port = parsed.port if parsed.port else (443 if use_https else 80)
        endpoint = parsed.path if parsed.path else '/'
        
        stats = {'success': 0, 'failed': 0, 'bytes': 0, 'times': []}
        stop_flag = threading.Event()
        lock = threading.Lock()
        
        def worker():
            while not stop_flag.is_set():
                try:
                    if use_https:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        s = context.wrap_socket(
                            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                            server_hostname=target
                        )
                    else:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    
                    s.settimeout(15)
                    s.connect((target, port))
                    
                    request = f"GET {endpoint} HTTP/1.1\r\n"
                    request += f"Host: {target}\r\n"
                    request += "User-Agent: Mozilla/5.0\r\n"
                    request += "Connection: close\r\n"
                    request += "\r\n"
                    
                    start = time.time()
                    s.send(request.encode())
                    
                    total = 0
                    while True:
                        try:
                            chunk = s.recv(16384)
                            if not chunk:
                                break
                            total += len(chunk)
                        except:
                            break
                    
                    response_time = time.time() - start
                    s.close()
                    
                    with lock:
                        stats['success'] += 1
                        stats['bytes'] += total
                        stats['times'].append(response_time)
                        
                except Exception as e:
                    with lock:
                        stats['failed'] += 1
                    time.sleep(0.1)
        
        print(f"\n{Fore.CYAN}Testing: {Fore.WHITE}{url}")
        print(f"  Threads: {threads}, Duration: {duration}s")
        
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads_list.append(t)
        
        start_time = time.time()
        
        # Progress indicator
        try:
            while time.time() - start_time < duration:
                time.sleep(1)
                elapsed = time.time() - start_time
                with lock:
                    sys.stdout.write(f"\r\033[K")
                    sys.stdout.write(
                        f"{Fore.CYAN}[{elapsed:.0f}s] "
                        f"{Fore.GREEN}Success: {stats['success']} "
                        f"{Fore.RED}Failed: {stats['failed']} "
                        f"{Fore.YELLOW}Data: {stats['bytes']/1024:.1f} KB"
                    )
                    sys.stdout.flush()
            stop_flag.set()
            
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Stopped")
            stop_flag.set()
        
        for t in threads_list:
            t.join(timeout=2)
        
        elapsed = time.time() - start_time
        print()  # New line after progress
        
        total_mb = stats['bytes'] / (1024 * 1024)
        avg_bandwidth = total_mb / elapsed if elapsed > 0 else 0
        success_rate = (stats['success'] / max(1, stats['success'] + stats['failed']) * 100)
        avg_response = (sum(stats['times']) / len(stats['times']) * 1000) if stats['times'] else 0
        
        return {
            'url': url,
            'threads': threads,
            'duration': duration,
            'total_requests': stats['success'] + stats['failed'],
            'success': stats['success'],
            'failed': stats['failed'],
            'success_rate': success_rate,
            'total_mb': total_mb,
            'avg_bandwidth': avg_bandwidth,
            'avg_response_ms': avg_response,
            'elapsed': elapsed
        }

def main():
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}🚀 OPTIMIZED BANDWIDTH TESTER")
    print(f"{Fore.CYAN}{'='*60}")
    
    # Input URL
    print(f"\n{Fore.WHITE}📝 Masukkan Target URL:")
    print(f"{Fore.LIGHTBLACK_EX}Contoh: https://gav-yam.co.il atau http://example.com")
    url = input(f"{Fore.GREEN}➜ {Fore.WHITE}URL: ").strip()
    
    if not url:
        print(f"{Fore.RED}[!] URL tidak boleh kosong!")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # Parse URL untuk validasi
    parsed = urlparse(url)
    if not parsed.hostname:
        print(f"{Fore.RED}[!] URL tidak valid!")
        return
    
    print(f"{Fore.GREEN}[✓] Target: {Fore.WHITE}{parsed.hostname}:{parsed.port if parsed.port else (443 if parsed.scheme == 'https' else 80)}")
    
    # Test config
    print(f"\n{Fore.WHITE}📋 Pilih Konfigurasi Testing:")
    print(f"  {Fore.LIGHTBLACK_EX}1. {Fore.WHITE}Quick Test  {Fore.LIGHTBLACK_EX}(5 threads, 10 detik)")
    print(f"  {Fore.LIGHTBLACK_EX}2. {Fore.WHITE}Medium Test {Fore.LIGHTBLACK_EX}(10 threads, 20 detik)")
    print(f"  {Fore.LIGHTBLACK_EX}3. {Fore.WHITE}Custom")
    
    choice = input(f"{Fore.GREEN}➜ {Fore.WHITE}Pilih (1/2/3): ").strip()
    
    if choice == '1':
        threads, duration = 5, 10
    elif choice == '2':
        threads, duration = 10, 20
    else:
        threads_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Jumlah Thread (default: 5): ").strip()
        threads = int(threads_input) if threads_input else 5
        
        duration_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Durasi detik (default: 10): ").strip()
        duration = int(duration_input) if duration_input else 10
    
    # Show config
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}📋 Konfigurasi:")
    print(f"   {Fore.LIGHTBLACK_EX}├─ Target:   {Fore.LIGHTWHITE_EX}{url}")
    print(f"   {Fore.LIGHTBLACK_EX}├─ Threads:  {Fore.LIGHTWHITE_EX}{threads}")
    print(f"   {Fore.LIGHTBLACK_EX}└─ Durasi:   {Fore.LIGHTWHITE_EX}{duration} detik")
    print(f"{Fore.CYAN}{'='*60}")
    
    confirm = input(f"\n{Fore.GREEN}➜ {Fore.WHITE}Mulai testing? (y/n): ").strip().lower()
    if confirm != 'y':
        print(f"{Fore.YELLOW}[!] Dibatalkan")
        return
    
    # Run test
    tester = OptimizedTester()
    result = tester.test_single(url, threads, duration)
    
    # Show results
    print(f"\n\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}📊 HASIL TESTING")
    print(f"{Fore.CYAN}{'='*60}")
    
    print(f"\n{Fore.WHITE}📈 Statistics:")
    print(f"   {Fore.GREEN}├─ Total Data:    {result['total_mb']:>8.2f} MB")
    print(f"   {Fore.GREEN}├─ Total Req:     {result['total_requests']:>8}")
    print(f"   {Fore.GREEN}├─ Success:       {result['success']:>8} ({result['success_rate']:.1f}%)")
    print(f"   {Fore.GREEN}├─ Failed:        {result['failed']:>8}")
    print(f"   {Fore.GREEN}└─ Duration:      {result['elapsed']:>8.2f}s")
    
    print(f"\n{Fore.WHITE}⚡ Bandwidth Metrics:")
    print(f"   {Fore.YELLOW}├─ Average Speed: {result['avg_bandwidth']:>8.2f} MB/s")
    print(f"   {Fore.YELLOW}└─ Throughput:    {result['avg_bandwidth']*8:>8.1f} Mbps")
    
    print(f"\n{Fore.WHITE}⏱️ Response Time:")
    print(f"   {Fore.LIGHTBLUE_EX}└─ Average:      {result['avg_response_ms']:>8.1f} ms")
    
    # Rating
    print(f"\n{Fore.WHITE}🎯 Performance Rating:")
    if result['avg_bandwidth'] >= 5:
        rating = f"{Fore.GREEN}🏆 Excellent (5+ MB/s)"
    elif result['avg_bandwidth'] >= 2:
        rating = f"{Fore.LIGHTGREEN_EX}✅ Good (2-5 MB/s)"
    elif result['avg_bandwidth'] >= 0.5:
        rating = f"{Fore.YELLOW}⚡ Average (0.5-2 MB/s)"
    elif result['avg_bandwidth'] >= 0.1:
        rating = f"{Fore.LIGHTYELLOW_EX}📶 Below Average (0.1-0.5 MB/s)"
    else:
        rating = f"{Fore.RED}❌ Slow (<0.1 MB/s)"
    print(f"   {rating}")
    
    # Tips
    print(f"\n{Fore.WHITE}💡 Tips:")
    if result['avg_bandwidth'] < 0.1:
        print(f"   {Fore.YELLOW}├─ Bandwidth sangat rendah. Coba:")
        print(f"   {Fore.YELLOW}│  - Kurangi threads menjadi 2-3")
        print(f"   {Fore.YELLOW}│  - Gunakan HTTP instead of HTTPS")
        print(f"   {Fore.YELLOW}│  - Periksa koneksi internet Anda")
        print(f"   {Fore.YELLOW}└─ Server mungkin berada di lokasi jauh")
    elif result['avg_response_ms'] > 5000:
        print(f"   {Fore.YELLOW}├─ Response time sangat tinggi (>5s)")
        print(f"   {Fore.YELLOW}│  - Server mungkin overload")
        print(f"   {Fore.YELLOW}└─ Coba testing dengan threads lebih sedikit")
    else:
        print(f"   {Fore.GREEN}├─ Performa cukup baik")
        print(f"   {Fore.GREEN}└─ Server responsif")
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.LIGHTBLACK_EX}Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save option
    save = input(f"\n{Fore.WHITE}💾 Simpan hasil? (y/n): ").strip().lower()
    if save == 'y':
        import json
        from datetime import datetime
        
        filename = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"{Fore.GREEN}[+] Hasil disimpan ke {filename}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Testing dihentikan")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}")
        sys.exit(1)
