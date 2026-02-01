"""
L2 以太网帧解析器
"""
import struct
from typing import Optional


class EtherType:
    """以太网类型常量"""
    IPv4 = 0x0800
    IPv6 = 0x86DD
    ARP = 0x0806


class EthernetFrame:
    """以太网帧结构"""
    def __init__(self, dst_mac: str, src_mac: str, ether_type: int, payload: bytes):
        self.dst_mac = dst_mac
        self.src_mac = src_mac
        self.ether_type = ether_type
        self.payload = payload


class EthernetParser:
    """
    以太网帧解析器
    解析 L2 以太网帧头部并提取负载
    """
    
    ETHERNET_HEADER_SIZE = 14
    
    @staticmethod
    def parse(data: bytes) -> Optional[EthernetFrame]:
        """
        解析以太网帧
        
        以太网帧格式（14字节头部）:
        - 目标 MAC (6 bytes)
        - 源 MAC (6 bytes)
        - 类型 (2 bytes)
        
        Args:
            data: 以太网帧数据
            
        Returns:
            EthernetFrame 对象，如果解析失败返回 None
        """
        if len(data) < EthernetParser.ETHERNET_HEADER_SIZE:
            return None
        
        try:
            # 提取 MAC 地址
            dst_mac = ':'.join(f'{b:02x}' for b in data[0:6])
            src_mac = ':'.join(f'{b:02x}' for b in data[6:12])
            
            # 提取以太网类型（大端序）
            ether_type = struct.unpack('!H', data[12:14])[0]
            
            #提取负载
            payload = data[14:]
            
            return EthernetFrame(dst_mac, src_mac, ether_type, payload)
        except struct.error:
            return None
