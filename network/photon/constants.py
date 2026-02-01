"""
Photon 网络协议常量定义
包含 Photon 相关的端口、协议标识等常量
"""

class PhotonPorts:
    """
    Photon 协议默认端口
    基于 Albion Online 的实际使用配置
    """
    # UDP 端口（Photon 主要使用 UDP）
    UDP = {5055, 5056, 5058}
    
    # TCP 端口（备用）
    TCP = {4530, 4531, 4533}
    
    @classmethod
    def is_photon_port(cls, port: int, protocol: str = "udp") -> bool:
        """
        检查端口是否为 Photon 端口
        
        Args:
            port: 端口号
            protocol: 协议类型 ("udp" 或 "tcp")
            
        Returns:
            如果是 Photon 端口返回 True
        """
        if protocol.lower() == "udp":
            return port in cls.UDP
        elif protocol.lower() == "tcp":
            return port in cls.TCP
        return False


class PhotonSignatures:
    """
    Photon 数据包负载特征
    用于识别非标准端口上的 Photon 数据
    """
    # Photon 数据包首字节常见特征
    MAGIC_BYTES = {0xF1, 0xF2, 0xFE}
    
    # 最小 Photon 负载长度
    MIN_PAYLOAD_LENGTH = 3

    # Photon 协议头长度
    PHOTON_HEADER_LENGTH = 12
