#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北科教館《十五年的約定》雲端穿透與手機 4G/5G 掃碼啟動器
- 支援區域網路 QR Code (展場 WiFi)
- 支援免費 Cloudflare Tunnel / Localtunnel (訪客自備 4G/5G 網路免連現場 WiFi)
"""

import sys
import os
import socket
import subprocess
import time

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def print_qr_hint(url):
    print("=" * 60)
    print("🌟【台北科教館 • 訪客手機連線指引】🌟")
    print(f"👉 存取網址： {url}")
    print("📱 請參觀學童/家長打開手機相機掃描下方 QR 碼即可直接遊玩：")
    print("=" * 60)
    try:
        import urllib.request
        api_url = f"http://qrenco.de/{url}"
        req = urllib.request.urlopen(api_url, timeout=3)
        print(req.read().decode('utf-8'))
    except Exception:
        print(f"[請直接於手機瀏覽器輸入網址：{url}]")

def main():
    port = 8000
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{port}"
    
    print("\n啟動雙軌連線模式...")
    print(f"[1] 展場區域網路模式：{local_url}")
    print(f"[2] 訪客自備 4G/5G 網路模式：可透過 cloudflared / npx localtunnel 穿透")
    
    print_qr_hint(local_url)

if __name__ == "__main__":
    main()
