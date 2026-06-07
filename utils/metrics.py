"""
System metrics collector using psutil
"""

import time
import socket
import subprocess
import psutil


class SystemMetrics:
    """Collect and format system metrics"""
    
    def __init__(self):
        self._prev_net = None
        self._prev_net_time = None
    
    def get_cpu_percent(self):
        """Get CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    def get_memory_info(self):
        """Get memory usage info"""
        mem = psutil.virtual_memory()
        return {
            'percent': mem.percent,
            'used_mb': mem.used / (1024 * 1024),
            'total_mb': mem.total / (1024 * 1024),
            'available_mb': mem.available / (1024 * 1024)
        }
    
    def get_disk_usage(self):
        """Get root disk usage"""
        disk = psutil.disk_usage('/')
        return {
            'percent': disk.percent,
            'used_gb': disk.used / (1024 * 1024 * 1024),
            'total_gb': disk.total / (1024 * 1024 * 1024),
            'free_gb': disk.free / (1024 * 1024 * 1024)
        }
    
    def get_temperature(self):
        """Get CPU temperature"""
        try:
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                return temps['cpu_thermal'][0].current
            elif 'coretemp' in temps:
                return temps['coretemp'][0].current
            else:
                # Try reading from thermal zone
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    return float(f.read().strip()) / 1000.0
        except Exception:
            return 0.0
    
    def get_uptime(self):
        """Get system uptime as formatted string"""
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d{hours:02d}h"
        elif hours > 0:
            return f"{hours}h{minutes:02d}m"
        else:
            return f"{minutes}m"
    
    def get_load_average(self):
        """Get system load average"""
        try:
            load1, load5, load15 = psutil.getloadavg()
            return load1, load5, load15
        except Exception:
            return 0.0, 0.0, 0.0
    
    def get_network_speed(self):
        """Get network upload/download speed in KB/s"""
        current_net = psutil.net_io_counters()
        current_time = time.time()
        
        if self._prev_net and self._prev_net_time:
            time_diff = current_time - self._prev_net_time
            if time_diff > 0:
                upload_speed = (current_net.bytes_sent - self._prev_net.bytes_sent) / time_diff / 1024
                download_speed = (current_net.bytes_recv - self._prev_net.bytes_recv) / time_diff / 1024
            else:
                upload_speed = 0
                download_speed = 0
        else:
            upload_speed = 0
            download_speed = 0
        
        self._prev_net = current_net
        self._prev_net_time = current_time
        
        return {
            'upload_kb': upload_speed,
            'download_kb': download_speed
        }
    
    def get_ip_address(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def get_wifi_signal(self):
        """Get WiFi signal strength"""
        try:
            result = subprocess.run(
                ['iw', 'dev', 'wlan0', 'station', 'dump'],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.split('\n'):
                if 'signal:' in line:
                    parts = line.split('signal:')
                    if len(parts) > 1:
                        dbm = parts[1].strip().split()[0]
                        return int(float(dbm))
        except Exception:
            pass
        return -100

    def get_wifi_info(self):
        """Get WiFi connection info"""
        info = {'connected': False, 'ssid': '', 'signal_dbm': -100, 'speed': ''}
        try:
            # Check if connected via ip command
            result = subprocess.run(
                ['ip', 'addr', 'show', 'wlan0'],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.split('\n'):
                if 'inet ' in line and 'state UP' in result.stdout:
                    info['connected'] = True
                elif 'state UP' in line:
                    info['connected'] = True

            # Try to get SSID
            result = subprocess.run(
                ['iw', 'dev', 'wlan0', 'link'],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.split('\n'):
                if 'SSID:' in line:
                    info['ssid'] = line.split('SSID:')[1].strip()
                elif 'Connected to' in line:
                    info['connected'] = True

            # Try to get signal
            result = subprocess.run(
                ['iw', 'dev', 'wlan0', 'station', 'dump'],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.split('\n'):
                if 'signal:' in line:
                    parts = line.split('signal:')
                    if len(parts) > 1:
                        dbm = parts[1].strip().split()[0]
                        info['signal_dbm'] = int(float(dbm))

            return info
        except Exception:
            return info
    
    def get_all_metrics(self):
        """Get all system metrics"""
        return {
            'cpu_percent': self.get_cpu_percent(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_usage(),
            'temperature': self.get_temperature(),
            'uptime': self.get_uptime(),
            'load_avg': self.get_load_average(),
            'network': self.get_network_speed(),
            'ip': self.get_ip_address(),
            'wifi': self.get_wifi_info()
        }
