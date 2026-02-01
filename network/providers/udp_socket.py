import socket
from typing import Optional, List
from threading import Thread, Event
from base.base2 import PacketProvider, RawPacketSignal

class UdpSocketProvider(PacketProvider):
    """
    UDP Socket 数据包提供者
    
    通过标准 Socket 监听本地端口，接收来自 Go Sniffer 转发的数据包
    """
    
    def __init__(self, signal: RawPacketSignal, target_ports: Optional[List[int]] = None, listening_port: int = 44444, host: str = '0.0.0.0'):
        super().__init__(signal)
        # target_ports 在这里不用于监听，仅作为参考或逻辑兼容
        self.listening_port = listening_port
        self._is_running = False
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._socket: Optional[socket.socket] = None
        self._host = host
        
    def start(self) -> bool:
        if self._is_running:
            return True
            
        try:
            self._stop_event.clear()
            
            # 创建单一接收 Socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 绑定到本地环回地址，接收 Go Sniffer 转发的数据
            sock.bind((self._host, self.listening_port))
            sock.settimeout(1.0) # 设置超时，以便线程可以响应停止信号
            self._socket = sock
            print(f"[UdpSocketProvider] 正在监听 {self._host}:{self.listening_port}")
            
            self._is_running = True
            self._thread = Thread(target=self._worker, daemon=True)
            self._thread.start()
            return True
            
        except Exception as e:
            print(f"[UdpSocketProvider] 启动失败: {e}")
            self.stop()
            return False
            
    def stop(self) -> bool:
        self._is_running = False
        self._stop_event.set()
        
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
            
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None
        
        return True
        
    def is_running(self) -> bool:
        return self._is_running
        
    def _worker(self):
        """工作线程：轮询 Socket 接收数据"""
        print("[UdpSocketProvider] 工作线程已启动")
        
        while not self._stop_event.is_set():
            if not self._socket:
                break
            try:
                data, addr = self._socket.recvfrom(65536)
                if data:
                    # 直接发射数据包，Go Sniffer 已经过滤了 Photon 协议
                    self.emit(data)
            except socket.timeout:
                continue
            except Exception as e:
                if self._is_running:
                    print(f"[UdpSocketProvider] 接收错误: {e}")
                        
        print("[UdpSocketProvider] 工作线程已停止")
