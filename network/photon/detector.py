"""
Photon 数据包检测器
识别 Photon 协议的数据包
"""
from network.photon.constants import PhotonPorts, PhotonSignatures


class PhotonDetector:
    """
    Photon 协议检测器
    通过端口和负载特征双重验证识别 Photon 数据包
    """
    
    @staticmethod
    def looks_like_photon(payload: bytes) -> bool:
        """
        通过负载特征判断是否为 Photon 数据
        
        Args:
            payload: UDP 负载数据
            
        Returns:
            如果负载特征匹配 Photon 返回 True
        """
        if len(payload) < PhotonSignatures.MIN_PAYLOAD_LENGTH:
            return False
        
        # 检查首字节是否匹配 Photon 魔数
        first_byte = payload[0]
        return first_byte in PhotonSignatures.MAGIC_BYTES
    
    @staticmethod
    def is_photon_packet(src_port: int, dst_port: int, payload: bytes) -> bool:
        """
        综合判断是否为 Photon 数据包
        
        Args:
            src_port: 源端口
            dst_port: 目标端口
            payload: UDP 负载数据
            
        Returns:
            如果是 Photon 数据包返回 True
        """
        # 端口匹配
        port_match = (
            PhotonPorts.is_photon_port(src_port, "udp") or 
            PhotonPorts.is_photon_port(dst_port, "udp")
        )
        
        # 负载特征匹配
        signature_match = PhotonDetector.looks_like_photon(payload)
        
        # 端口或特征任一匹配即可
        is_photon = port_match or signature_match
        
        # 但负载不能为空
        return is_photon and len(payload) > 0
