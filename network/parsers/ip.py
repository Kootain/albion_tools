"""
L3 IP 数据包解析器  
支持 IPv4 和 IPv6
"""
import struct
from typing import Optional
from enum import IntEnum


class IPProtocol(IntEnum):
    """IP 协议类型"""
    TCP = 6
    UDP = 17


class IPv4Packet:
    """IPv4 数据包结构"""
    def __init__(self, protocol: int, src_addr: str, dst_addr: str, payload: bytes):
        self.protocol = protocol
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.payload = payload


class IPv6Packet:
    """IPv6 数据包结构"""
    def __init__(self, next_header: int, src_addr: str, dst_addr: str, payload: bytes):
        self.next_header = next_header
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.payload = payload


class IPParser:
    """
    IP 数据包解析器
    支持 IPv4 和 IPv6
    """
    
    @staticmethod
    def parse_ipv4(data: bytes) -> Optional[IPv4Packet]:
        """
        解析 IPv4 数据包
        
        Args:
            data: IPv4 数据包数据
            
        Returns:
            IPv4Packet 对象，如果解析失败返回 None
        """
        if len(data) < 20:  # IPv4 最小头部长度
            return None
        
        try:
            # 提取版本和头部长度
            version_ihl = data[0]
            version = (version_ihl >> 4) & 0x0F
            if version != 4:
                return None
            
            ihl = (version_ihl & 0x0F) * 4  # IHL 以 4 字节为单位
            
            # 提取协议
            protocol = data[9]
            
            # 提取源和目标 IP 地址
            src_addr = '.'.join(str(b) for b in data[12:16])
            dst_addr = '.'.join(str(b) for b in data[16:20])
            
            # 提取负载（跳过头部）
            payload = data[ihl:]
            
            return IPv4Packet(protocol, src_addr, dst_addr, payload)
        except (IndexError, struct.error):
            return None
    
    @staticmethod
    def parse_ipv6(data: bytes) -> Optional[IPv6Packet]:
        """
        解析 IPv6 数据包（简化版）
        
        Args:
            data: IPv6 数据包数据
            
        Returns:
            IPv6Packet 对象，如果解析失败返回 None
        """
        if len(data) < 40:  # IPv6 固定头部长度
            return None
        
        try:
            # 提取 Next Header (Byte 6)
            next_header = data[6]
            
            # 提取地址（简化为十六进制表示）
            src_addr = data[8:24].hex()
            dst_addr = data[24:40].hex()
            
            # 负载从 Byte 40 开始
            payload = data[40:]
            
            return IPv6Packet(next_header, src_addr, dst_addr, payload)
        except (IndexError, struct.error):
            return None
