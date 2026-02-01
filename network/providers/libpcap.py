"""
基于 Npcap 的数据包提供者实现
参考 C# LibpcapPacketProvider 的企业级设计
"""
from this import d
import pcapy
import time
import threading
from typing import Optional, Dict, List

from pydantic.type_adapter import P
from base.base2 import PacketProvider, RawPacketSignal
from network.parsers.ethernet import EthernetParser, EtherType
from network.parsers.ip import IPParser, IPProtocol
from network.parsers.udp import UDPParser
from network.photon.detector import PhotonDetector
from network.providers.device_type import get_network_interface_types


class DeviceLockManager:
    """
    设备锁定管理器
    实现首包锁定和超时释放机制
    """
    def __init__(self, score_to_lock: int = 1, lock_timeout: float = 20.0):
        self._active_device: Optional[str] = None
        self._device_scores: Dict[str, int] = {}
        self._last_valid_time: float = 0
        self._lock_timeout = lock_timeout
        self._score_to_lock = score_to_lock
        self._lock = threading.Lock()
    
    def select_and_lock(self, device_name: str) -> bool:
        """
        为设备打分并可能锁定
        
        Returns:
            如果当前设备被激活返回 True
        """
        with self._lock:
            # 检查超时释放
            if self._active_device and time.time() - self._last_valid_time > self._lock_timeout:
                print(f"[DeviceLockManager] 释放锁定设备（超时）")
                self._active_device = None
                self._device_scores.clear()
            
            # 如果已锁定其他设备，拒绝
            if self._active_device and self._active_device != device_name:
                return False
            
            # 为设备打分
            self._device_scores[device_name] = self._device_scores.get(device_name, 0) + 1
            
            # 达到分数阈值，锁定设备
            if self._device_scores[device_name] >= self._score_to_lock:
                if not self._active_device:
                    self._active_device = device_name
                    print(f"[DeviceLockManager] 锁定设备: {device_name}")
                
                self._last_valid_time = time.time()
                return True
            
            return self._active_device is None
    
    def is_active_device(self, device_name: str) -> bool:
        """检查是否为当前激活设备"""
        with self._lock:
            return self._active_device is None or self._active_device == device_name


class LibpcapProvider(PacketProvider):
    """
    基于 Npcap/Libpcap 的数据包提供者
    实现多设备管理、智能锁定、分层解析等企业级特性
    """
    
    def __init__(self, signal: RawPacketSignal, target_ports: Optional[List[int]] = None):
        super().__init__(signal)

        self.target_ports = target_ports
        self._captures: Dict[str, pcapy.pcapy] = {}
        self._device_type: Dict[str, any] = {}
        self._stop_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._lock_manager = DeviceLockManager()
    
    def start(self) -> bool:
        """启动数据包捕获"""
        if self.is_running():
            print("[LibpcapProvider] 已在运行")
            return False
        
        try:
            # 查找所有可用设备
            devices = pcapy.findalldevs()
            device_types = get_network_interface_types()
            for device in device_types:
                self._device_type[device.name] = device
            if not devices:
                print("[LibpcapProvider] 错误: 未找到网络设备，请安装 Npcap")
                return False
            
            # 打开所有可用设备
            opened_count = 0
            for i, device in enumerate(devices):
                try:
                    # 打开设备
                    cap = pcapy.open_live(device, 65536, False, 100)
                    
                    # 设置 BPF 过滤器
                    if self.target_ports:
                        filter_str = f'udp port {self.target_ports[0]}'
                        for port in self.target_ports[1:]:
                            filter_str += f' or udp port {port}'
                        cap.setfilter(filter_str)
                        print(f"[LibpcapProvider][{i}] {device}: 过滤器 = {filter_str}")
                    
                    self._captures[device] = cap
                    opened_count += 1
                    print(f"[LibpcapProvider][{i}] 打开设备: {device} ({self._device_type[device]})")
                    
                except Exception as e:
                    print(f"[LibpcapProvider][{i}] 打开设备失败 {device}: {e}")
            
            if opened_count == 0:
                print("[LibpcapProvider] 错误: 无法打开任何设备")
                return False
            
            # 启动工作线程
            self._stop_event.clear()
            self._worker_thread = threading.Thread(target=self._worker, daemon=True)
            self._worker_thread.start()
            
            print(f"[LibpcapProvider] 数据包捕获已启动，打开 {opened_count} 个设备")
            return True
            
        except Exception as e:
            print(f"[LibpcapProvider] 启动失败: {e}")
            return False
    
    def stop(self) -> bool:
        """停止数据包捕获"""
        if not self.is_running():
            return False
        
        try:
            self._stop_event.set()
            if self._worker_thread:
                self._worker_thread.join(timeout=2.0)
            
            # 关闭所有设备
            for device, cap in self._captures.items():
                try:
                    cap.close()
                except:
                    pass
            
            self._captures.clear()
            self._worker_thread = None
            
            print("[LibpcapProvider] 数据包捕获已停止")
            return True
        except Exception as e:
            print(f"[LibpcapProvider] 停止失败: {e}")
            return False
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._worker_thread is not None and self._worker_thread.is_alive()
    
    def _worker(self):
        """工作线程：轮询所有设备并分发数据"""
        print("[LibpcapProvider] 工作线程已启动")
        
        while not self._stop_event.is_set():
            try:
                dispatched = 0
                
                # 轮询所有设备
                for device, cap in list(self._captures.items()):
                    if not self._lock_manager.is_active_device(device):
                        continue
                    try:
                        header, raw_data = cap.next()
                        if header:
                            self._dispatch(device, raw_data)
                            dispatched += 1
                    except pcapy.PcapError:
                        continue
                
                # 无数据时短暂休眠
                if dispatched == 0:
                    time.sleep(0.025)  # 25ms
            except ValueError:
                pass
                    
            # except Exception as e:
            #     print(f"[LibpcapProvider] 工作线程错误: {e}")
            #     time.sleep(0.1)
        
        print("[LibpcapProvider] 工作线程已退出")

    def _handle_uu_route(self, raw_data: bytes):
        """
        处理 UU 路由模式数据包
        """
        if len(raw_data) < 1:
            return None
        
        version = (raw_data[0] >> 4) & 0x0F
        if version == 4:
            return IPParser.parse_ipv4(raw_data)
        elif version == 6:
            return IPParser.parse_ipv6(raw_data)
        return None        
    
    def _dispatch(self, device: str, raw_data: bytes):
        """
        分发数据包：分层解析并识别 Photon
        
        Args:
            device: 设备名称
            raw_data: 原始数据包
        """
        # L2: 解析以太网帧

        device_info = self._device_type[device]
        ip_packet = None
        if device_info.if_type == 53: # UU 路由模式
            ip_packet = self._handle_uu_route(raw_data)
        else:
            eth_frame = EthernetParser.parse(raw_data)
            if not eth_frame:
                return        
            # 根据以太网类型选择 L3 解析
            if eth_frame.ether_type == EtherType.IPv4:
                ip_packet = IPParser.parse_ipv4(eth_frame.payload)
            elif eth_frame.ether_type == EtherType.IPv6:
                ip_packet = IPParser.parse_ipv6(eth_frame.payload)
            else:
                return

        if not ip_packet:
            return
        
        # L4: 仅处理 UDP
        protocol = ip_packet.protocol if hasattr(ip_packet, 'protocol') else ip_packet.next_header
        if protocol != IPProtocol.UDP:
            return
        
        udp_packet = UDPParser.parse(ip_packet.payload)
        if not udp_packet:
            return

        if not PhotonDetector.is_photon_packet(
            udp_packet.src_port,
            udp_packet.dst_port,
            udp_packet.payload,
        ):
            return

        # 设备锁定管理
        if not self._lock_manager.select_and_lock(device):
            return  # 被其他设备锁定
        
        if not self._lock_manager.is_active_device(device):
            return
        
        # 发布事件
        self.emit(udp_packet.payload)
