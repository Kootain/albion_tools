"""
网络管理器
整合 SnifferWorker 和 HandlerRegistry，对外提供统一的网络管理接口
类似于 C# 的 NetworkManager
"""
from network.providers.libpcap import LibpcapProvider
from network.providers.udp_socket import UdpSocketProvider
from typing import Optional, List
from base.base2 import RawPacketSignal
from core.config.storage import global_config_manager

class NetworkManager:
    """
    网络管理器
    负责启动/停止网络抓包，管理 Handler 注册表
    """
    
    def __init__(self, target_ports: Optional[List[int]] = None):
        """
        初始化网络管理器
        
        Args:
            event_bus: 事件总线实例，如果为 None 则使用全局实例
            target_port: 目标监听端口
        """
        self.target_ports = target_ports
        
        self.packet_provider: Optional[object] = None # LibpcapProvider or UdpSocketProvider
        
        print("[NetworkManager] 网络管理器已初始化")

    
    def start(self, signal: RawPacketSignal) -> bool:
        """
        启动网络抓包
        
        Returns:
            如果启动成功返回 True，否则返回 False
        """
        if self.packet_provider and self.packet_provider.is_running():
            print("[NetworkManager] 数据包提供者已在运行")
            return False
        
        try:
            # 读取配置决定使用哪种模式
            mode = global_config_manager.get_setting("general", "sniffer_mode", "local")
            
            if mode == "remote":
                print("[NetworkManager] 使用远程/Go转发模式 (UDP Socket)")
                # 监听端口 44444，与 Go Sniffer config.json 中的 targets 对应
                self.packet_provider = UdpSocketProvider(signal=signal, target_ports=self.target_ports, listening_port=44444)
            else:
                print("[NetworkManager] 使用本地抓包模式 (Libpcap)")
                self.packet_provider = LibpcapProvider(signal=signal, target_ports=self.target_ports)
                
            success = self.packet_provider.start()
            
            if success:
                print(f"[NetworkManager] 网络抓包已启动 (端口: {self.target_ports or '全部'})")
            
            return success
        except Exception as e:
            print(f"[NetworkManager] 启动失败: {e}")
            return False
    
    def stop(self) -> bool:
        """
        停止网络抓包
        
        Returns:
            如果停止成功返回 True，否则返回 False
        """
        if not self.packet_provider or not self.packet_provider.is_running():
            print("[NetworkManager] 数据包提供者未在运行")
            return False
        
        try:
            success = self.packet_provider.stop()
            self.packet_provider = None
            
            if success:
                print("[NetworkManager] 网络抓包已停止")
            
            return success
        except Exception as e:
            print(f"[NetworkManager] 停止失败: {e}")
            return False
    
    def is_running(self) -> bool:
        """
        检查网络抓包是否正在运行
        
        Returns:
            如果正在运行返回 True，否则返回 False
        """
        return self.packet_provider is not None and self.packet_provider.is_running()
    