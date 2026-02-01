"""
L4 UDP 数据包解析器
"""
import struct
from typing import Optional, Tuple


class UDPPacket:
    """UDP 数据包结构"""
    def __init__(self, src_port: int, dst_port: int, length: int, checksum: int, payload: bytes):
        self.src_port = src_port
        self.dst_port = dst_port
        self.length = length
        self.checksum = checksum
        self.payload = payload


class UDPParser:
    """
    UDP 数据包解析器
    解析 UDP 头部（8字节）并提取负载
    """
    
    UDP_HEADER_SIZE = 8
    
    @staticmethod
    def parse(data: bytes) -> Optional[UDPPacket]:
        """
        解析 UDP 数据包
        
        UDP 头部格式（8字节）:
        - 源端口 (2 bytes)
        - 目标端口 (2 bytes)
        - 长度 (2 bytes)
        - 校验和 (2 bytes)
        
        Args:
            data: UDP 数据包（包含头部和负载）
            
        Returns:
            UDPPacket 对象，如果解析失败返回 None
        """
        if len(data) < UDPParser.UDP_HEADER_SIZE:
            return None
        
        try:
            # 解析 UDP 头部（大端序）
            src_port, dst_port, length, checksum = struct.unpack('!HHHH', data[:8])
            
            # 提取负载
            payload = data[8:]
            
            return UDPPacket(src_port, dst_port, length, checksum, payload)
        except struct.error:
            return None
