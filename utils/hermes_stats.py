"""
Hermes Agent statistics collector
"""

import os
import time
import subprocess
import psutil

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class HermesStats:
    """Collect Hermes Agent statistics"""
    
    def __init__(self):
        self._process_cache = None
        self._cache_time = 0
        self._cache_duration = 2.0  # Cache for 2 seconds
    
    def _find_hermes_process(self):
        """Find Hermes Agent process"""
        current_time = time.time()
        
        # Use cached result if still valid
        if self._process_cache and (current_time - self._cache_time) < self._cache_duration:
            try:
                if self._process_cache.is_running():
                    return self._process_cache
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self._process_cache = None
        
        # Search for hermes process
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info.get('cmdline', []) or [])
                proc_name = proc.info.get('name', '')
                
                # Check for hermes process
                if ('hermes' in proc_name.lower() or 
                    'hermes' in cmdline.lower()):
                    # Skip our own monitor process
                    if 'opiz2w-monitor' not in cmdline and 'monitor.py' not in cmdline:
                        self._process_cache = proc
                        self._cache_time = current_time
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self._process_cache = None
        return None
    
    def is_running(self):
        """Check if Hermes Agent is running"""
        proc = self._find_hermes_process()
        return proc is not None
    
    def get_pid(self):
        """Get Hermes process PID"""
        proc = self._find_hermes_process()
        if proc:
            return proc.pid
        return None
    
    def get_memory_mb(self):
        """Get Hermes memory usage in MB"""
        proc = self._find_hermes_process()
        if proc:
            try:
                mem = proc.memory_info()
                return mem.rss / (1024 * 1024)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return 0.0
    
    def get_cpu_percent(self):
        """Get Hermes CPU usage"""
        proc = self._find_hermes_process()
        if proc:
            try:
                return proc.cpu_percent(interval=0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return 0.0
    
    def get_uptime(self):
        """Get Hermes process uptime"""
        proc = self._find_hermes_process()
        if proc:
            try:
                create_time = proc.create_time()
                uptime_seconds = time.time() - create_time
                
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                
                if days > 0:
                    return f"{days}d{hours:02d}h"
                elif hours > 0:
                    return f"{hours}h{minutes:02d}m"
                else:
                    return f"{minutes}m"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return "N/A"
    
    def get_gateway_status(self):
        """Check Hermes Gateway status"""
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'hermes-gateway'],
                capture_output=True, text=True, timeout=2
            )
            return result.stdout.strip() == 'active'
        except Exception:
            return False
    
    def get_session_count(self):
        """Get number of active sessions (approximate)"""
        try:
            # Try to count session files in hermes directory
            sessions_dir = os.path.expanduser('~/.hermes/sessions')
            if os.path.exists(sessions_dir):
                count = len([f for f in os.listdir(sessions_dir) 
                           if f.endswith('.json')])
                return count
        except Exception:
            pass
        return 0
    
    def get_version(self):
        """Get Hermes version"""
        try:
            result = subprocess.run(
                ['hermes', '--version'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"
    
    def get_all_stats(self):
        """Get all Hermes statistics"""
        return {
            'running': self.is_running(),
            'pid': self.get_pid(),
            'memory_mb': self.get_memory_mb(),
            'cpu_percent': self.get_cpu_percent(),
            'uptime': self.get_uptime(),
            'gateway_running': self.get_gateway_status(),
            'sessions': self.get_session_count(),
            'version': self.get_version()
        }
