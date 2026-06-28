#!/usr/bin/env python3
"""
MULTI-ENDPOINT BANDWIDTH TESTER - FULL VERSION
Dengan Auto Generator, Validasi, dan Testing Multi Endpoint
"""

import socket
import ssl
import threading
import time
import sys
import random
import json
import signal
from datetime import datetime
from urllib.parse import urlparse
from colorama import init, Fore, Style
from collections import defaultdict

init(autoreset=True)

# ============ KONFIGURASI ============
class Config:
    VERSION = "3.0"
    MAX_THREADS = 500
    DEFAULT_THREADS = 50
    DEFAULT_DURATION = 30
    DEFAULT_CHUNK_SIZE = 16384
    TIMEOUT = 30
    VALIDATION_TIMEOUT = 5

# ============ ENDPOINT GENERATOR ============
class EndpointGenerator:
    """Generate endpoints berdasarkan kategori"""
    
    COMMON = ['/', '/index.html', '/index.php', '/home', '/main']
    API = ['/api', '/api/v1', '/api/users', '/api/products', '/api/health', '/api/ping']
    STATIC = ['/css/style.css', '/js/app.js', '/images/logo.png', '/favicon.ico']
    WORDPRESS = ['/wp-admin', '/wp-login.php', '/wp-json', '/wp-content/themes']
    ECOMMERCE = ['/shop', '/products', '/cart', '/checkout', '/my-account']
    SOCIAL = ['/login', '/register', '/profile', '/feed', '/messages']
    FILES = ['/robots.txt', '/sitemap.xml', '/downloads/file.zip', '/uploads/doc.pdf']
    ADMIN = ['/admin', '/admin/dashboard', '/admin/users']
    
    CATEGORIES = {
        'all': COMMON + API + STATIC + WORDPRESS + ECOMMERCE + SOCIAL + FILES + ADMIN,
        'common': COMMON,
        'api': API,
        'static': STATIC,
        'wordpress': WORDPRESS,
        'ecommerce': ECOMMERCE,
        'social': SOCIAL,
        'files': FILES,
        'admin': ADMIN
    }
    
    @classmethod
    def generate(cls, base_url, category='all'):
        endpoints = cls.CATEGORIES.get(category, cls.CATEGORIES['all'])
        return [f"{base_url}{ep}" for ep in endpoints]
    
    @classmethod
    def get_categories(cls):
        return list(cls.CATEGORIES.keys())

        # ============ ENDPOINT VALIDATOR ============
class EndpointValidator:
    """Validasi endpoint sebelum testing"""
    
    @staticmethod
    def validate(url, timeout=5):
        try:
            parsed = urlparse(url)
            target = parsed.hostname
            use_https = parsed.scheme == 'https'
            port = parsed.port if parsed.port else (443 if use_https else 80)
            endpoint = parsed.path if parsed.path else '/'
            
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
            
            s.settimeout(timeout)
            s.connect((target, port))
            
            request = f"HEAD {endpoint} HTTP/1.1\r\n"
            request += f"Host: {target}\r\n"
            request += "Connection: close\r\n"
            request += "\r\n"
            
            s.send(request.encode())
            
            response = b""
            try:
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    response += chunk
            except:
                pass
            
            s.close()
            
            response_str = response.decode('utf-8', errors='ignore')
            valid_codes = ['200', '301', '302', '304', '307', '308']
            return any(code in response_str for code in valid_codes)
            
        except Exception:
            return False
    
    @staticmethod
    def validate_multiple(endpoints, show_progress=True):
        """Validasi multiple endpoints"""
        valid = []
        invalid = []
        
        for i, endpoint in enumerate(endpoints, 1):
            if show_progress:
                print(f"  [{i}/{len(endpoints)}] Checking: {endpoint[:50]}...", end=" ")
            
            if EndpointValidator.validate(endpoint):
                if show_progress:
                    print(f"{Fore.GREEN}✓ VALID")
                valid.append(endpoint)
            else:
                if show_progress:
                    print(f"{Fore.RED}✗ INVALID")
                invalid.append(endpoint)
        
        return valid, invalid

        # ============ HTTP REQUESTER ============
class HttpRequester:
    def __init__(self, target, port, use_https, chunk_size=16384, keep_alive=True, verbose=False):
        self.target = target
        self.port = port
        self.use_https = use_https
        self.chunk_size = chunk_size
        self.keep_alive = keep_alive
        self.verbose = verbose
    
    def generate_user_agent(self):
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(agents)
    
    def request(self, url, timeout=30):
        """Send HTTP request and return response"""
        start_time = time.time()
        s = None
        
        try:
            parsed = urlparse(url)
            target = parsed.hostname or self.target
            use_https = parsed.scheme == 'https' if parsed.scheme else self.use_https
            port = parsed.port if parsed.port else (443 if use_https else 80)
            endpoint = parsed.path if parsed.path else '/'
            if parsed.query:
                endpoint += f"?{parsed.query}"
            
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
            
            s.settimeout(timeout)
            s.connect((target, port))
            
            request = f"GET {endpoint} HTTP/1.1\r\n"
            request += f"Host: {target}\r\n"
            request += f"User-Agent: {self.generate_user_agent()}\r\n"
            request += "Accept: */*\r\n"
            
            if self.keep_alive:
                request += "Connection: keep-alive\r\n"
            else:
                request += "Connection: close\r\n"
            request += "\r\n"
            
            s.send(request.encode())
            
            total_bytes = 0
            while True:
                try:
                    chunk = s.recv(self.chunk_size)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                except:
                    break
            
            response_time = time.time() - start_time
            s.close()
            
            return {
                'success': True,
                'bytes': total_bytes,
                'time': response_time,
                'endpoint': endpoint
            }
            
        except Exception as e:
            if self.verbose:
                print(f"Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'endpoint': endpoint if 'endpoint' in locals() else 'unknown'
            }
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass
# ============ STATS MANAGER ============
class StatsManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.reset()
    
    def reset(self):
        self.stats = {
            'total_bytes': 0,
            'total_requests': 0,
            'success_requests': 0,
            'failed_requests': 0,
            'start_time': None,
            'end_time': None,
            'response_times': [],
            'status_codes': defaultdict(int),
            'bandwidth_history': [],
            'endpoint_stats': defaultdict(lambda: {'success': 0, 'failed': 0, 'bytes': 0, 'times': []}),
            'total_duration': 0,
            'peak_bandwidth': 0
        }
    
    def update_bytes(self, bytes_count):
        with self.lock:
            self.stats['total_bytes'] += bytes_count
    
    def update_request(self, success=True, endpoint='unknown', bytes_count=0, response_time=0):
        with self.lock:
            self.stats['total_requests'] += 1
            if success:
                self.stats['success_requests'] += 1
                self.stats['endpoint_stats'][endpoint]['success'] += 1
                self.stats['endpoint_stats'][endpoint]['bytes'] += bytes_count
                self.stats['endpoint_stats'][endpoint]['times'].append(response_time)
                self.stats['response_times'].append(response_time)
                
                bandwidth = (bytes_count / 1024 / 1024) / response_time if response_time > 0 else 0
                if bandwidth > self.stats['peak_bandwidth']:
                    self.stats['peak_bandwidth'] = bandwidth
            else:
                self.stats['failed_requests'] += 1
                self.stats['endpoint_stats'][endpoint]['failed'] += 1
    
    def update_bandwidth(self, bandwidth):
        with self.lock:
            self.stats['bandwidth_history'].append(bandwidth)
    
    def get_stats(self):
        with self.lock:
            return self.stats.copy()
    
    def get_endpoint_stats(self):
        with self.lock:
            return dict(self.stats['endpoint_stats'])

   # ============ UI HELPER ============
class UIHelper:
    @staticmethod
    def print_header(title, version="3.0"):
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}🚀 {title} v{version}")
        print(f"{Fore.CYAN}{'='*70}")
    
    @staticmethod
    def print_config(config):
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}📋 Konfigurasi Testing:")
        for key, value in config.items():
            print(f"   {Fore.LIGHTBLACK_EX}├─ {key}: {Fore.LIGHTWHITE_EX}{value}")
        print(f"{Fore.CYAN}{'='*70}")
    
    @staticmethod
    def get_input(prompt, default=None, input_type=str):
        if default is not None:
            prompt = f"{prompt} (default: {default})"
        
        user_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}{prompt}: ").strip()
        
        if not user_input and default is not None:
            return default
        
        if input_type == int:
            try:
                return int(user_input)
            except:
                return default
        elif input_type == bool:
            return user_input.lower() in ['y', 'yes', 'true', '1']
        else:
            return user_input if user_input else default
    
    @staticmethod
    def confirm(prompt="Mulai testing? (y/n)"):
        return UIHelper.get_input(prompt, default='n', input_type=bool)

        # ============ MAIN TESTER ============
class MultiEndpointTester:
    def __init__(self):
        self.target = None
        self.port = None
        self.use_https = False
        self.base_url = None
        self.threads = Config.DEFAULT_THREADS
        self.duration = Config.DEFAULT_DURATION
        self.test_mode = 'mixed'
        self.chunk_size = Config.DEFAULT_CHUNK_SIZE
        self.keep_alive = True
        self.verbose = False
        self.endpoints = []
        self.valid_endpoints = []
        self.stats_manager = StatsManager()
        self.stop_flag = threading.Event()
    
    def parse_url(self, url):
        if not url:
            return False
        
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        try:
            parsed = urlparse(url)
            if not parsed.hostname:
                return False
            
            self.target = parsed.hostname
            self.use_https = parsed.scheme == 'https'
            self.port = parsed.port if parsed.port else (443 if self.use_https else 80)
            self.base_url = f"{'https' if self.use_https else 'http'}://{self.target}"
            if self.port not in [80, 443]:
                self.base_url += f":{self.port}"
            
            if self.target and ':' in self.target:
                self.target = self.target.split(':')[0]
            
            return True
            
        except Exception:
            return False
    
    def worker(self):
        requester = HttpRequester(
            target=self.target,
            port=self.port,
            use_https=self.use_https,
            chunk_size=self.chunk_size,
            keep_alive=self.keep_alive,
            verbose=self.verbose
        )
        
        while not self.stop_flag.is_set():
            if self.valid_endpoints:
                endpoint = random.choice(self.valid_endpoints)
                result = requester.request(endpoint)
                
                if result['success']:
                    self.stats_manager.update_request(
                        success=True,
                        endpoint=result['endpoint'],
                        bytes_count=result['bytes'],
                        response_time=result['time']
                    )
                    self.stats_manager.update_bytes(result['bytes'])
                else:
                    self.stats_manager.update_request(
                        success=False,
                        endpoint=result['endpoint']
                    )
            time.sleep(0.001)
    
    def monitor(self):
        last_bytes = 0
        last_time = time.time()
        last_requests = 0
        
        while not self.stop_flag.is_set():
            time.sleep(1)
            current_time = time.time()
            
            stats = self.stats_manager.get_stats()
            current_bytes = stats['total_bytes']
            current_requests = stats['total_requests']
            elapsed = current_time - last_time
            
            bandwidth = ((current_bytes - last_bytes) / (1024 * 1024)) / elapsed if elapsed > 0 else 0
            self.stats_manager.update_bandwidth(bandwidth)
            
            total_mb = current_bytes / (1024 * 1024)
            total_gb = total_mb / 1024
            avg_bandwidth = sum(stats['bandwidth_history']) / len(stats['bandwidth_history']) if stats['bandwidth_history'] else 0
            rps = (current_requests - last_requests) / elapsed if elapsed > 0 else 0
            
            sys.stdout.write(f"\r\033[K")
            sys.stdout.write(
                f"{Fore.CYAN}📊 {Fore.WHITE}Data: {Fore.GREEN}{total_mb:.1f} MB "
                f"{Fore.LIGHTBLACK_EX}({total_gb:.2f} GB) "
                f"{Fore.YELLOW}| Speed: {Fore.LIGHTGREEN_EX}{bandwidth:.2f} MB/s "
                f"{Fore.LIGHTBLACK_EX}(avg: {avg_bandwidth:.2f}) "
                f"{Fore.MAGENTA}| Req: {current_requests} "
                f"{Fore.LIGHTBLACK_EX}| RPS: {rps:.1f} "
                f"{Fore.LIGHTBLACK_EX}| Thr: {self.threads}"
            )
            sys.stdout.flush()
            
            last_bytes = current_bytes
            last_requests = current_requests
            last_time = current_time
    
    def interactive_input(self):
        UIHelper.print_header("MULTI-ENDPOINT BANDWIDTH TESTER", Config.VERSION)
        
        # Target URL
        print(f"\n{Fore.WHITE}📝 Masukkan Target URL:")
        print(f"{Fore.LIGHTBLACK_EX}Contoh: https://www.ronijablo.co.il")
        
        while True:
            url_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}URL: ").strip()
            if not url_input:
                print(f"{Fore.RED}[!] URL tidak boleh kosong!")
                continue
            
            if self.parse_url(url_input):
                print(f"{Fore.GREEN}[✓] Target: {Fore.WHITE}{self.target}:{self.port}")
                break
            else:
                print(f"{Fore.RED}[!] URL tidak valid, coba lagi")
        
        # Endpoint method
        print(f"\n{Fore.WHITE}📋 Pilih Metode Endpoint:")
        print(f"  {Fore.LIGHTBLACK_EX}1. {Fore.WHITE}Auto Generate {Fore.LIGHTBLACK_EX}- Generate endpoints otomatis")
        print(f"  {Fore.LIGHTBLACK_EX}2. {Fore.WHITE}Manual Input  {Fore.LIGHTBLACK_EX}- Input manual")
        print(f"  {Fore.LIGHTBLACK_EX}3. {Fore.WHITE}Single Test   {Fore.LIGHTBLACK_EX}- Test 1 endpoint saja")
        
        method = input(f"{Fore.GREEN}➜ {Fore.WHITE}Pilih (1/2/3): ").strip()
        
        if method == '1':
            # Auto generate
            print(f"\n{Fore.WHITE}📋 Pilih Kategori:")
            categories = EndpointGenerator.get_categories()
            for i, cat in enumerate(categories, 1):
                print(f"  {Fore.LIGHTBLACK_EX}{i}. {Fore.WHITE}{cat.capitalize()}")
            
            cat_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Pilih kategori (1-{len(categories)}): ").strip()
            try:
                idx = int(cat_input) - 1
                category = categories[idx] if 0 <= idx < len(categories) else 'all'
            except:
                category = 'all'
            
            self.endpoints = EndpointGenerator.generate(self.base_url, category)
            print(f"{Fore.GREEN}[✓] Generated {len(self.endpoints)} endpoints")
            
        elif method == '3':
            # Single test
            print(f"\n{Fore.WHITE}📝 Masukkan endpoint (default: /):")
            endpoint = input(f"{Fore.GREEN}➜ {Fore.WHITE}Endpoint: ").strip()
            if not endpoint:
                endpoint = '/'
            self.endpoints = [f"{self.base_url}{endpoint}"]
            
        else:
            # Manual input
            print(f"\n{Fore.WHITE}📝 Masukkan endpoints (pisah dengan koma):")
            print(f"{Fore.LIGHTBLACK_EX}Contoh: /,/api,/robots.txt,/about")
            endpoints_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Endpoints: ").strip()
            
            if endpoints_input:
                endpoints = [e.strip() for e in endpoints_input.split(',')]
                self.endpoints = [f"{self.base_url}{e}" if e.startswith('/') else e for e in endpoints]
            else:
                self.endpoints = [f"{self.base_url}/"]
        
        # Validate endpoints
        if len(self.endpoints) > 1:
            validate = input(f"\n{Fore.WHITE}🔍 Validasi endpoint? (y/n, default: y): ").strip().lower()
            if validate != 'n':
                print(f"\n{Fore.YELLOW}🔍 Validasi {len(self.endpoints)} endpoints...")
                valid, invalid = EndpointValidator.validate_multiple(self.endpoints)
                self.valid_endpoints = valid
                
                print(f"\n{Fore.CYAN}{'='*60}")
                print(f"{Fore.WHITE}📊 Hasil Validasi:")
                print(f"   {Fore.GREEN}✓ Valid:   {len(valid)} endpoints")
                print(f"   {Fore.RED}✗ Invalid: {len(invalid)} endpoints")
                print(f"{Fore.CYAN}{'='*60}")
                
                if not self.valid_endpoints:
                    print(f"{Fore.RED}[!] Tidak ada endpoint valid, menggunakan semua endpoint")
                    self.valid_endpoints = self.endpoints
            else:
                self.valid_endpoints = self.endpoints
        else:
            self.valid_endpoints = self.endpoints
        
        # Threads
        self.threads = UIHelper.get_input("🧵 Jumlah Thread", Config.DEFAULT_THREADS, int)
        if self.threads > Config.MAX_THREADS:
            print(f"{Fore.YELLOW}[!] Membatasi ke {Config.MAX_THREADS} threads")
            self.threads = Config.MAX_THREADS
        
        # Duration
        self.duration = UIHelper.get_input("⏱️ Durasi (detik)", Config.DEFAULT_DURATION, int)
        
        # Mode
        print(f"\n{Fore.WHITE}📋 Mode Testing:")
        print(f"  {Fore.LIGHTBLACK_EX}1. {Fore.WHITE}Mixed     {Fore.LIGHTBLACK_EX}- Kombinasi")
        print(f"  {Fore.LIGHTBLACK_EX}2. {Fore.WHITE}Download  {Fore.LIGHTBLACK_EX}- GET saja")
        print(f"  {Fore.LIGHTBLACK_EX}3. {Fore.WHITE}Upload    {Fore.LIGHTBLACK_EX}- POST saja")
        print(f"  {Fore.LIGHTBLACK_EX}4. {Fore.WHITE}Both      {Fore.LIGHTBLACK_EX}- GET + POST")
        
        mode_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Pilih mode (1-4): ").strip()
        mode_map = {'1': 'mixed', '2': 'download', '3': 'upload', '4': 'both'}
        self.test_mode = mode_map.get(mode_input, 'mixed')
        
        # Chunk size
        self.chunk_size = UIHelper.get_input("📦 Chunk Size (bytes)", Config.DEFAULT_CHUNK_SIZE, int)
        
        # Keep-alive
        self.keep_alive = UIHelper.get_input("🔗 Keep-Alive? (y/n)", 'y', bool)
        
        # Verbose
        self.verbose = UIHelper.get_input("📝 Verbose? (y/n)", 'n', bool)
        
        # Show config
        config = {
            "Target": f"{self.target}:{self.port}",
            "Protocol": 'HTTPS' if self.use_https else 'HTTP',
            "Endpoints": f"{len(self.valid_endpoints)} valid dari {len(self.endpoints)} total",
            "Threads": self.threads,
            "Durasi": f"{self.duration} detik",
            "Mode": self.test_mode.upper(),
            "Chunk Size": f"{self.chunk_size} bytes",
            "Keep-Alive": 'Yes' if self.keep_alive else 'No'
        }
        UIHelper.print_config(config)
        
        return UIHelper.confirm()
    
    def run(self):
        if not self.interactive_input():
            print(f"{Fore.YELLOW}[!] Dibatalkan")
            return
        
        print(f"\n{Fore.YELLOW}⚡ Testing {len(self.valid_endpoints)} endpoints... Press Ctrl+C to stop\n")
        
        self.stats_manager.reset()
        self.stats_manager.stats['start_time'] = time.time()
        
        threads_list = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads_list.append(t)
        
        monitor_thread = threading.Thread(target=self.monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            time.sleep(self.duration)
            self.stop_flag.set()
        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}[!] Test interrupted")
            self.stop_flag.set()
        
        for t in threads_list:
            t.join(timeout=2)
        
        self.stats_manager.stats['end_time'] = time.time()
        self.stats_manager.stats['total_duration'] = self.stats_manager.stats['end_time'] - self.stats_manager.stats['start_time']
        
        self.show_results()
    
    def show_results(self):
        stats = self.stats_manager.get_stats()
        elapsed = stats['total_duration']
        total_mb = stats['total_bytes'] / (1024 * 1024)
        avg_bandwidth = total_mb / elapsed if elapsed > 0 else 0
        success_rate = (stats['success_requests'] / max(1, stats['total_requests']) * 100)
        
        print(f"\n\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}📊 MULTI-ENDPOINT TEST RESULTS")
        print(f"{Fore.CYAN}{'='*70}")
        
        print(f"\n{Fore.WHITE}📈 Overall Statistics:")
        print(f"   {Fore.GREEN}├─ Total Data:       {total_mb:>10.2f} MB")
        print(f"   {Fore.GREEN}├─ Total Requests:   {stats['total_requests']:>10}")
        print(f"   {Fore.GREEN}├─ Success:          {stats['success_requests']:>10} ({success_rate:.1f}%)")
        print(f"   {Fore.GREEN}├─ Failed:           {stats['failed_requests']:>10}")
        print(f"   {Fore.GREEN}└─ Duration:         {elapsed:>10.2f} detik")
        
        print(f"\n{Fore.WHITE}⚡ Bandwidth Metrics:")
        print(f"   {Fore.YELLOW}├─ Average Speed:    {avg_bandwidth:>10.2f} MB/s")
        print(f"   {Fore.YELLOW}├─ Peak Speed:       {stats['peak_bandwidth']:>10.2f} MB/s")
        print(f"   {Fore.YELLOW}└─ Throughput:       {avg_bandwidth*8:>10.1f} Mbps")
        
        if stats['response_times']:
            avg_response = sum(stats['response_times']) / len(stats['response_times']) * 1000
            print(f"\n{Fore.WHITE}⏱️ Response Times:")
            print(f"   {Fore.LIGHTBLUE_EX}└─ Average:        {avg_response:>10.1f} ms")
        
        endpoint_stats = self.stats_manager.get_endpoint_stats()
        if len(endpoint_stats) > 1:
            print(f"\n{Fore.WHITE}📊 Per-Endpoint Results:")
            print(f"{Fore.LIGHTBLACK_EX}{'─'*60}")
            print(f"{Fore.CYAN}Endpoint{' ':<30} │ Success │ Failed │ Size(KB)")
            print(f"{Fore.LIGHTBLACK_EX}{'─'*60}")
            
            for endpoint, data in sorted(endpoint_stats.items(), key=lambda x: x[1]['success'], reverse=True)[:10]:
                ep_display = endpoint[:30] + '...' if len(endpoint) > 30 else endpoint
                total = data['success'] + data['failed']
                avg_size = data['bytes'] / max(1, total) / 1024
                color = Fore.GREEN if data['success'] > data['failed'] else Fore.RED
                print(f"{Fore.WHITE}{ep_display:<30} │ {color}{data['success']:>3}/{total:<3} │ {data['failed']:>6} │ {avg_size:>8.1f}")
        
        print(f"\n{Fore.WHITE}🎯 Performance Rating:")
        if avg_bandwidth >= 10:
            rating = f"{Fore.GREEN}🏆 Excellent (10+ MB/s)"
        elif avg_bandwidth >= 5:
            rating = f"{Fore.LIGHTGREEN_EX}✅ Great (5-10 MB/s)"
        elif avg_bandwidth >= 2:
            rating = f"{Fore.YELLOW}⚡ Good (2-5 MB/s)"
        elif avg_bandwidth >= 1:
            rating = f"{Fore.LIGHTYELLOW_EX}📶 Average (1-2 MB/s)"
        else:
            rating = f"{Fore.RED}❌ Slow (<1 MB/s)"
        print(f"   {rating}")
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.LIGHTBLACK_EX}Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.save_report(stats, elapsed, total_mb, avg_bandwidth)
    
    def save_report(self, stats, elapsed, total_mb, avg_bandwidth):
        report = {
            'tool': 'Multi-Endpoint Bandwidth Tester',
            'version': Config.VERSION,
            'timestamp': datetime.now().isoformat(),
            'target': f"{'https' if self.use_https else 'http'}://{self.target}:{self.port}",
            'config': {
                'threads': self.threads,
                'duration': self.duration,
                'mode': self.test_mode,
                'chunk_size': self.chunk_size,
                'keep_alive': self.keep_alive,
                'endpoints_tested': len(self.valid_endpoints)
            },
            'results': {
                'total_bytes': stats['total_bytes'],
                'total_mb': total_mb,
                'total_requests': stats['total_requests'],
                'success_requests': stats['success_requests'],
                'failed_requests': stats['failed_requests'],
                'success_rate': (stats['success_requests'] / max(1, stats['total_requests']) * 100),
                'duration_seconds': elapsed,
                'avg_bandwidth_mbps': avg_bandwidth,
                'peak_bandwidth_mbps': stats['peak_bandwidth'],
                'avg_response_ms': (sum(stats['response_times']) / len(stats['response_times']) * 1000) if stats['response_times'] else 0
            },
            'endpoint_stats': {
                ep: {
                    'success': data['success'],
                    'failed': data['failed'],
                    'bytes': data['bytes'],
                    'avg_response_ms': (sum(data['times']) / len(data['times']) * 1000) if data['times'] else 0
                }
                for ep, data in self.stats_manager.get_endpoint_stats().items()
            }
        }
        
        filename = f"multi_endpoint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"{Fore.GREEN}[+] Report saved to {filename}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error saving report: {e}")

     # ============ MAIN ============
def main():
    def signal_handler(sig, frame):
        print(f"\n{Fore.YELLOW}[!] Stopping...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    tester = MultiEndpointTester()
    tester.run()

if __name__ == "__main__":
    main()
    
                    
