#!/usr/bin/env python3
"""
HEAVY CONTENT TESTER - Untuk Website dengan Konten Berat
Testing bandwidth dengan file besar, gambar, video, dan konten berat lainnya
"""

import socket
import ssl
import threading
import time
import sys
import random
import json
import signal
import os
from datetime import datetime
from urllib.parse import urlparse
from colorama import init, Fore, Style
from collections import defaultdict

init(autoreset=True)

# ============ KONFIGURASI ============
class Config:
    VERSION = "2.0"
    MAX_THREADS = 200
    DEFAULT_THREADS = 20
    DEFAULT_DURATION = 30
    DEFAULT_CHUNK_SIZE = 65536  # 64KB untuk konten berat
    TIMEOUT = 60

# ============ HEAVY ENDPOINT GENERATOR ============
class HeavyEndpointGenerator:
    """Generate endpoints untuk konten berat"""
    
    # Large file extensions
    LARGE_FILES = [
        '/images/background.jpg',
        '/images/banner.jpg',
        '/images/slider-1.jpg',
        '/images/slider-2.jpg',
        '/images/hero.jpg',
        '/images/header.jpg',
        '/images/gallery/photo1.jpg',
        '/images/gallery/photo2.jpg',
        '/uploads/photo.jpg',
        '/uploads/image.png',
        '/assets/images/main-banner.jpg',
        '/assets/images/product-1.jpg',
        '/assets/images/product-2.jpg',
        '/media/images/cover.jpg',
        '/media/uploads/image.jpg',
        '/images/products/1.jpg',
        '/images/products/2.jpg',
        '/images/products/3.jpg',
    ]
    
    # Video files
    VIDEO_FILES = [
        '/videos/demo.mp4',
        '/videos/intro.mp4',
        '/videos/background.mp4',
        '/videos/tutorial.mp4',
        '/assets/videos/hero.mp4',
        '/assets/videos/promo.mp4',
        '/media/videos/sample.mp4',
        '/uploads/video.mp4',
        '/videos/stock-footage.mp4',
        '/assets/videos/background-loop.mp4',
    ]
    
    # Audio files
    AUDIO_FILES = [
        '/audio/background.mp3',
        '/audio/music.mp3',
        '/audio/soundtrack.mp3',
        '/assets/audio/theme.mp3',
        '/media/audio/sample.mp3',
        '/uploads/audio.mp3',
        '/audio/podcast.mp3',
    ]
    
    # Document files
    DOCUMENT_FILES = [
        '/documents/report.pdf',
        '/documents/brochure.pdf',
        '/documents/catalog.pdf',
        '/assets/files/datasheet.pdf',
        '/downloads/document.pdf',
        '/uploads/files/report.pdf',
        '/files/whitepaper.pdf',
        '/documents/presentation.pptx',
        '/documents/spreadsheet.xlsx',
    ]
    
    # Download files
    DOWNLOAD_FILES = [
        '/downloads/file.zip',
        '/downloads/software.zip',
        '/downloads/package.zip',
        '/downloads/archive.zip',
        '/assets/files/sample.zip',
        '/downloads/setup.exe',
        '/downloads/installer.msi',
        '/files/backup.zip',
        '/downloads/update.zip',
    ]
    
    # API endpoints with heavy data
    API_HEAVY = [
        '/api/users?limit=1000',
        '/api/products?limit=500&include=images',
        '/api/reports/monthly?format=json',
        '/api/analytics/dashboard?period=year',
        '/api/data/export?format=csv&limit=10000',
        '/api/statistics/detailed',
        '/api/logs/recent?count=1000',
        '/api/backup/download',
        '/api/reports/annual?format=pdf',
        '/api/export/all-users',
        '/api/dashboard/metrics',
        '/api/inventory/report',
    ]
    
    CATEGORIES = {
        'all': LARGE_FILES + VIDEO_FILES + AUDIO_FILES + DOCUMENT_FILES + DOWNLOAD_FILES + API_HEAVY,
        'images': LARGE_FILES,
        'videos': VIDEO_FILES,
        'audio': AUDIO_FILES,
        'documents': DOCUMENT_FILES,
        'downloads': DOWNLOAD_FILES,
        'api': API_HEAVY,
        'mixed': LARGE_FILES + API_HEAVY + DOWNLOAD_FILES
    }
    
    @classmethod
    def generate(cls, base_url, category='all'):
        endpoints = cls.CATEGORIES.get(category, cls.CATEGORIES['all'])
        return [f"{base_url}{ep}" for ep in endpoints]
    
    @classmethod
    def get_categories(cls):
        return list(cls.CATEGORIES.keys())

# ============ HEAVY TESTER ============
class HeavyContentTester:
    def __init__(self):
        self.target = None
        self.port = None
        self.use_https = False
        self.base_url = None
        self.threads = Config.DEFAULT_THREADS
        self.duration = Config.DEFAULT_DURATION
        self.chunk_size = Config.DEFAULT_CHUNK_SIZE
        self.keep_alive = True
        self.verbose = False
        self.endpoints = []
        self.test_mode = 'download'
        
        # Stats
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
            'endpoint_stats': defaultdict(lambda: {'success': 0, 'failed': 0, 'bytes': 0, 'times': [], 'max': 0}),
            'total_duration': 0,
            'peak_bandwidth': 0,
            'total_mb': 0,
            'avg_speed': 0
        }
        
        self.lock = threading.Lock()
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
    
    def generate_user_agent(self):
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        ]
        return random.choice(agents)
    
    def test_endpoint(self, url):
        """Test single endpoint - optimized for heavy content"""
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
            
            s.settimeout(Config.TIMEOUT)
            s.connect((target, port))
            
            # Request dengan range untuk file besar (partial download)
            range_header = None
            if random.random() > 0.3:  # 70% request menggunakan range
                sizes = ['0-1048575', '0-5242879', '0-10485759', '0-20971519']
                range_header = random.choice(sizes)
            
            request = f"GET {endpoint} HTTP/1.1\r\n"
            request += f"Host: {target}\r\n"
            request += f"User-Agent: {self.generate_user_agent()}\r\n"
            request += "Accept: */*\r\n"
            
            if range_header:
                request += f"Range: bytes={range_header}\r\n"
            
            if self.keep_alive:
                request += "Connection: keep-alive\r\n"
            else:
                request += "Connection: close\r\n"
            request += "\r\n"
            
            s.send(request.encode())
            
            total_bytes = 0
            chunks = []
            
            while True:
                try:
                    chunk = s.recv(self.chunk_size)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    total_bytes += len(chunk)
                    
                    with self.lock:
                        self.stats['total_bytes'] += len(chunk)
                        
                except socket.timeout:
                    break
                except:
                    break
            
            response_time = time.time() - start_time
            s.close()
            
            # Update stats
            endpoint_key = endpoint[:30] + '...' if len(endpoint) > 30 else endpoint
            with self.lock:
                self.stats['endpoint_stats'][endpoint_key]['bytes'] += total_bytes
                self.stats['endpoint_stats'][endpoint_key]['times'].append(response_time)
                self.stats['endpoint_stats'][endpoint_key]['success'] += 1
                if total_bytes > self.stats['endpoint_stats'][endpoint_key]['max']:
                    self.stats['endpoint_stats'][endpoint_key]['max'] = total_bytes
                
                self.stats['success_requests'] += 1
                self.stats['response_times'].append(response_time)
                self.stats['total_requests'] += 1
                
                # Bandwidth
                bandwidth = (total_bytes / 1024 / 1024) / response_time if response_time > 0 else 0
                if bandwidth > self.stats['peak_bandwidth']:
                    self.stats['peak_bandwidth'] = bandwidth
                
                self.stats['status_codes'][200] += 1
            
            return True
            
        except Exception as e:
            endpoint_key = endpoint[:30] + '...' if 'endpoint' in locals() and len(endpoint) > 30 else 'unknown'
            with self.lock:
                self.stats['endpoint_stats'][endpoint_key]['failed'] += 1
                self.stats['failed_requests'] += 1
                self.stats['total_requests'] += 1
                self.stats['status_codes'][404] += 1
            if self.verbose:
                print(f"{Fore.RED}[!] Error: {e}")
            return False
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass
    
    def worker(self):
        """Worker thread untuk heavy content"""
        while not self.stop_flag.is_set():
            if self.endpoints:
                endpoint = random.choice(self.endpoints)
                self.test_endpoint(endpoint)
            else:
                time.sleep(0.1)
    
    def monitor_bandwidth(self):
        """Monitor bandwidth real-time dengan detail"""
        last_bytes = 0
        last_time = time.time()
        last_requests = 0
        
        while not self.stop_flag.is_set():
            time.sleep(1)
            current_time = time.time()
            
            with self.lock:
                current_bytes = self.stats['total_bytes']
                current_requests = self.stats['total_requests']
                elapsed = current_time - last_time
                
                bandwidth = ((current_bytes - last_bytes) / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                self.stats['bandwidth_history'].append(bandwidth)
                
                total_mb = current_bytes / (1024 * 1024)
                total_gb = total_mb / 1024
                avg_bandwidth = sum(self.stats['bandwidth_history']) / len(self.stats['bandwidth_history']) if self.stats['bandwidth_history'] else 0
                rps = (current_requests - last_requests) / elapsed if elapsed > 0 else 0
                
                # Clear line
                sys.stdout.write(f"\r\033[K")
                
                # Main stats
                status_line = (
                    f"{Fore.CYAN}📊 {Fore.WHITE}Data: {Fore.GREEN}{total_mb:.1f} MB "
                    f"{Fore.LIGHTBLACK_EX}({total_gb:.2f} GB) "
                    f"{Fore.YELLOW}| Speed: {Fore.LIGHTGREEN_EX}{bandwidth:.2f} MB/s "
                    f"{Fore.LIGHTBLACK_EX}(avg: {avg_bandwidth:.2f}) "
                    f"{Fore.MAGENTA}| Req: {current_requests} "
                    f"{Fore.LIGHTBLACK_EX}| RPS: {rps:.1f} "
                    f"{Fore.LIGHTBLACK_EX}| Thr: {self.threads}"
                )
                
                # Add info about largest file
                if self.stats['endpoint_stats']:
                    max_endpoint = max(self.stats['endpoint_stats'].items(), key=lambda x: x[1]['max'])
                    if max_endpoint[1]['max'] > 0:
                        max_mb = max_endpoint[1]['max'] / (1024 * 1024)
                        status_line += f" {Fore.LIGHTBLACK_EX}| Max: {Fore.CYAN}{max_mb:.1f}MB"
                
                sys.stdout.write(status_line)
                sys.stdout.flush()
                
                last_bytes = current_bytes
                last_requests = current_requests
                last_time = current_time
    
    def interactive_input(self):
        """Input interaktif"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}🚀 HEAVY CONTENT BANDWIDTH TESTER v{Config.VERSION}")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.LIGHTBLACK_EX}Testing dengan file besar: Gambar, Video, Audio, Dokumen, API")
        print(f"{Fore.CYAN}{'='*70}")
        
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
        print(f"  {Fore.LIGHTBLACK_EX}1. {Fore.WHITE}Auto Generate {Fore.LIGHTBLACK_EX}- Generate konten berat otomatis")
        print(f"  {Fore.LIGHTBLACK_EX}2. {Fore.WHITE}Manual Input  {Fore.LIGHTBLACK_EX}- Input manual")
        print(f"  {Fore.LIGHTBLACK_EX}3. {Fore.WHITE}Single Test   {Fore.LIGHTBLACK_EX}- Test 1 endpoint saja")
        
        method = input(f"{Fore.GREEN}➜ {Fore.WHITE}Pilih (1/2/3): ").strip()
        
        if method == '1':
            # Auto generate
            print(f"\n{Fore.WHITE}📋 Pilih Kategori Konten Berat:")
            categories = HeavyEndpointGenerator.get_categories()
            for i, cat in enumerate(categories, 1):
                cat_name = cat.capitalize()
                if cat == 'images':
                    cat_name = 'Gambar (JPG, PNG)'
                elif cat == 'videos':
                    cat_name = 'Video (MP4)'
                elif cat == 'audio':
                    cat_name = 'Audio (MP3)'
                elif cat == 'documents':
                    cat_name = 'Dokumen (PDF, PPT)'
                elif cat == 'downloads':
                    cat_name = 'Download (ZIP, EXE)'
                elif cat == 'api':
                    cat_name = 'API (Data Besar)'
                elif cat == 'mixed':
                    cat_name = 'Campuran (Rekomendasi)'
                print(f"  {Fore.LIGHTBLACK_EX}{i}. {Fore.WHITE}{cat_name}")
            
            cat_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Pilih kategori (1-{len(categories)}): ").strip()
            try:
                idx = int(cat_input) - 1
                category = categories[idx] if 0 <= idx < len(categories) else 'mixed'
            except:
                category = 'mixed'
            
            self.endpoints = HeavyEndpointGenerator.generate(self.base_url, category)
            print(f"{Fore.GREEN}[✓] Generated {len(self.endpoints)} endpoints untuk konten berat")
            
        elif method == '3':
            # Single test
            print(f"\n{Fore.WHITE}📝 Masukkan endpoint untuk konten berat:")
            print(f"{Fore.LIGHTBLACK_EX}Contoh: /images/banner.jpg atau /videos/demo.mp4")
            endpoint = input(f"{Fore.GREEN}➜ {Fore.WHITE}Endpoint: ").strip()
            if not endpoint:
                endpoint = '/images/banner.jpg'
            self.endpoints = [f"{self.base_url}{endpoint}"]
            
        else:
            # Manual input
            print(f"\n{Fore.WHITE}📝 Masukkan endpoints untuk konten berat (pisah dengan koma):")
            print(f"{Fore.LIGHTBLACK_EX}Contoh: /images/banner.jpg,/videos/demo.mp4,/downloads/file.zip")
            endpoints_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Endpoints: ").strip()
            
            if endpoints_input:
                endpoints = [e.strip() for e in endpoints_input.split(',')]
                self.endpoints = [f"{self.base_url}{e}" if e.startswith('/') else e for e in endpoints]
            else:
                self.endpoints = [f"{self.base_url}/images/banner.jpg"]
        
        # Threads
        print(f"\n{Fore.WHITE}🧵 Jumlah Thread (default: 20):")
        print(f"{Fore.LIGHTBLACK_EX}Rekomendasi: 10-50 untuk konten berat")
        threads_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Threads: ").strip()
        if threads_input:
            try:
                self.threads = min(int(threads_input), Config.MAX_THREADS)
            except:
                print(f"{Fore.YELLOW}[!] Menggunakan default 20")
        
        # Duration
        print(f"\n{Fore.WHITE}⏱️  Durasi (detik, default: 30):")
        duration_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Durasi: ").strip()
        if duration_input:
            try:
                self.duration = int(duration_input)
            except:
                print(f"{Fore.YELLOW}[!] Menggunakan default 30")
        
        # Chunk size
        print(f"\n{Fore.WHITE}📦 Chunk Size (bytes, default: 65536):")
        print(f"{Fore.LIGHTBLACK_EX}Untuk konten berat, gunakan chunk besar: 32768, 65536, 131072")
        chunk_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Chunk Size: ").strip()
        if chunk_input:
            try:
                self.chunk_size = int(chunk_input)
            except:
                print(f"{Fore.YELLOW}[!] Menggunakan default 65536")
        
        # Keep-alive
        print(f"\n{Fore.WHITE}🔗 Keep-Alive? (y/n, default: y):")
        keep_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Keep-Alive: ").strip().lower()
        self.keep_alive = keep_input not in ['n', 'no']
        
        # Verbose
        print(f"\n{Fore.WHITE}📝 Verbose? (y/n, default: n):")
        verbose_input = input(f"{Fore.GREEN}➜ {Fore.WHITE}Verbose: ").strip().lower()
        self.verbose = verbose_input in ['y', 'yes']
        
        # Show config
        total_estimated = len(self.endpoints) * self.threads * self.duration / 10
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}📋 Konfigurasi Testing:")
        print(f"   {Fore.LIGHTBLACK_EX}├─ Target:     {Fore.LIGHTWHITE_EX}{self.target}:{self.port}")
        print(f"   {Fore.LIGHTBLACK_EX}├─ Protocol:   {Fore.LIGHTWHITE_EX}{'HTTPS' if self.use_https else 'HTTP'}")
        print(f"   {Fore.LIGHTBLACK_EX}├─ Endpoints:  {Fore.LIGHTWHITE_EX}{len(self.endpoints)} konten berat")
        if len(self.endpoints) <= 5:
            for ep in self.endpoints:
                print(f"   {Fore.LIGHTBLACK_EX}│  └─ {Fore.LIGHTWHITE_EX}{ep}")
        else:
            for ep in self.endpoints[:3]:
                print(f"   {Fore.LIGHTBLACK_EX}│  └─ {Fore.LIGHTWHITE_EX}{ep}")
            print(f"   {Fore.LIGHTBLACK_EX}│  └─ {Fore.LIGHTWHITE_EX}... dan {len(self.endpoints)-3} lainnya")
        print(f"   {Fore.LIGHTBLACK_EX}├─ Threads:    {Fore.LIGHTWHITE_EX}{self.threads}")
        print(f"   {Fore.LIGHTBLACK_EX}├─ Durasi:     {Fore.LIGHTWHITE_EX}{self.duration} detik")
        print(f"   {Fore.LIGHTBLACK_EX}├─ Chunk Size: {Fore.LIGHTWHITE_EX}{self.chunk_size} bytes")
        print(f"   {Fore.LIGHTBLACK_EX}├─ Keep-Alive: {Fore.LIGHTWHITE_EX}{'Yes' if self.keep_alive else 'No'}")
        print(f"   {Fore.LIGHTBLACK_EX}└─ Est. Data:  {Fore.LIGHTWHITE_EX}~{total_estimated/1024:.1f} MB - {total_estimated/10:.1f} MB")
        print(f"{Fore.CYAN}{'='*70}")
        
        confirm = input(f"\n{Fore.GREEN}➜ {Fore.WHITE}Mulai testing? (y/n): ").strip().lower()
        return confirm in ['y', 'yes']
    
    def run(self):
        """Main runner"""
        if not self.interactive_input():
            print(f"{Fore.YELLOW}[!] Dibatalkan")
            return
        
        print(f"\n{Fore.YELLOW}⚡ Testing {len(self.endpoints)} endpoints konten berat... Press Ctrl+C to stop")
        print(f"{Fore.LIGHTBLACK_EX}   Maksimum bandwidth dengan file besar\n")
        
        # Reset stats
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
            'endpoint_stats': defaultdict(lambda: {'success': 0, 'failed': 0, 'bytes': 0, 'times': [], 'max': 0}),
            'total_duration': 0,
            'peak_bandwidth': 0,
            'total_mb': 0,
            'avg_speed': 0
        }
        
        self.stats['start_time'] = time.time()
        
        # Start threads
        threads_list = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads_list.append(t)
        
        # Start monitor
        monitor_thread = threading.Thread(target=self.monitor_bandwidth)
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
        
        self.stats['end_time'] = time.time()
        self.stats['total_duration'] = self.stats['end_time'] - self.stats['start_time']
        self.stats['total_mb'] = self.stats['total_bytes'] / (1024 * 1024)
        self.stats['avg_speed'] = self.stats['total_mb'] / self.stats['total_duration'] if self.stats['total_duration'] > 0 else 0
        
        self.show_results()
    
    def show_results(self):
        """Display results dengan fokus pada konten berat"""
        stats = self.stats
        elapsed = stats['total_duration']
        total_mb = stats['total_mb']
        avg_bandwidth = stats['avg_speed']
        success_rate = (stats['success_requests'] / max(1, stats['total_requests']) * 100)
        
        print(f"\n\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}📊 HEAVY CONTENT TEST RESULTS")
        print(f"{Fore.CYAN}{'='*70}")
        
        print(f"\n{Fore.WHITE}📈 Transfer Statistics:")
        print(f"   {Fore.GREEN}├─ Total Data:       {total_mb:>10.2f} MB ({total_mb/1024:.2f} GB)")
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
            min_response = min(stats['response_times']) * 1000
            max_response = max(stats['response_times']) * 1000
            
            print(f"\n{Fore.WHITE}⏱️ Response Times:")
            print(f"   {Fore.LIGHTBLUE_EX}├─ Average:        {avg_response:>10.1f} ms")
            print(f"   {Fore.LIGHTBLUE_EX}├─ Minimum:        {min_response:>10.1f} ms")
            print(f"   {Fore.LIGHTBLUE_EX}└─ Maximum:        {max_response:>10.1f} ms")
        
        # Per-endpoint stats
        endpoint_stats = dict(stats['endpoint_stats'])
        if endpoint_stats:
            print(f"\n{Fore.WHITE}📊 Per-Endpoint Results (Terbesar):")
            print(f"{Fore.LIGHTBLACK_EX}{'─'*70}")
            print(f"{Fore.CYAN}Endpoint{' ':<30} │ Success │ Failed │ Total(MB) │ Max(MB) │ Avg(KB)")
            print(f"{Fore.LIGHTBLACK_EX}{'─'*70}")
            
            sorted_endpoints = sorted(endpoint_stats.items(), key=lambda x: x[1]['bytes'], reverse=True)[:10]
            for endpoint, data in sorted_endpoints:
                ep_display = endpoint[:30] + '...' if len(endpoint) > 30 else endpoint
                total = data['success'] + data['failed']
                total_mb_ep = data['bytes'] / (1024 * 1024)
                max_mb_ep = data['max'] / (1024 * 1024)
                avg_kb = (data['bytes'] / max(1, total)) / 1024
                color = Fore.GREEN if data['success'] > data['failed'] else Fore.RED
                print(f"{Fore.WHITE}{ep_display:<30} │ {color}{data['success']:>3}/{total:<3} │ {data['failed']:>6} │ {total_mb_ep:>8.1f} │ {max_mb_ep:>7.1f} │ {avg_kb:>8.1f}")
        
        # Bandwidth history
        if stats['bandwidth_history']:
            print(f"\n{Fore.WHITE}📈 Bandwidth History (last 20 samples):")
            history = stats['bandwidth_history'][-20:]
            max_val = max(history) if history else 1
            
            for i, val in enumerate(history):
                bar_length = int((val / max_val) * 30) if max_val > 0 else 0
                bar = '█' * bar_length
                print(f"   {Fore.CYAN}{i+1:2}s {Fore.GREEN}{bar} {val:.2f} MB/s")
        
        # Performance rating untuk konten berat
        print(f"\n{Fore.WHITE}🎯 Performance Rating (Konten Berat):")
        if avg_bandwidth >= 10:
            rating = f"{Fore.GREEN}🏆 Excellent (10+ MB/s) - Server sangat cepat untuk konten berat"
        elif avg_bandwidth >= 5:
            rating = f"{Fore.LIGHTGREEN_EX}✅ Great (5-10 MB/s) - Server cepat untuk konten berat"
        elif avg_bandwidth >= 2:
            rating = f"{Fore.YELLOW}⚡ Good (2-5 MB/s) - Server cukup cepat"
        elif avg_bandwidth >= 1:
            rating = f"{Fore.LIGHTYELLOW_EX}📶 Average (1-2 MB/s) - Server sedang"
        elif avg_bandwidth >= 0.5:
            rating = f"{Fore.MAGENTA}🐌 Below Average (0.5-1 MB/s) - Server lambat untuk konten berat"
        else:
            rating = f"{Fore.RED}❌ Slow (<0.5 MB/s) - Server sangat lambat"
        print(f"   {rating}")
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.LIGHTBLACK_EX}Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save report
        self.save_report()
    
    def save_report(self):
        """Save detailed report"""
        stats = self.stats
        
        report = {
            'tool': 'Heavy Content Bandwidth Tester',
            'version': Config.VERSION,
            'timestamp': datetime.now().isoformat(),
            'target': f"{'https' if self.use_https else 'http'}://{self.target}:{self.port}",
            'config': {
                'threads': self.threads,
                'duration': self.duration,
                'chunk_size': self.chunk_size,
                'keep_alive': self.keep_alive,
                'endpoints_tested': len(self.endpoints),
                'test_type': 'heavy_content'
            },
            'results': {
                'total_bytes': stats['total_bytes'],
                'total_mb': stats['total_mb'],
                'total_requests': stats['total_requests'],
                'success_requests': stats['success_requests'],
                'failed_requests': stats['failed_requests'],
                'success_rate': (stats['success_requests'] / max(1, stats['total_requests']) * 100),
                'duration_seconds': stats['total_duration'],
                'avg_bandwidth_mbps': stats['avg_speed'],
                'peak_bandwidth_mbps': stats['peak_bandwidth'],
                'avg_response_ms': (sum(stats['response_times']) / len(stats['response_times']) * 1000) if stats['response_times'] else 0,
                'total_mb_transferred': stats['total_mb']
            },
            'endpoint_stats': {
                ep: {
                    'success': data['success'],
                    'failed': data['failed'],
                    'bytes': data['bytes'],
                    'max_bytes': data['max'],
                    'avg_response_ms': (sum(data['times']) / len(data['times']) * 1000) if data['times'] else 0
                }
                for ep, data in stats['endpoint_stats'].items()
            },
            'bandwidth_history': stats['bandwidth_history'][-100:]
        }
        
        filename = f"heavy_content_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    
    tester = HeavyContentTester()
    tester.run()

if __name__ == "__main__":
    main()
