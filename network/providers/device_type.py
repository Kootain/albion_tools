import ctypes
from enum import IntEnum
from dataclasses import dataclass
from typing import List, Optional
import platform

def is_windows():
    return platform.system() == "Windows"

if is_windows():
    from ctypes import wintypes

class NetworkInterfaceType(IntEnum):
    # The interface type is not known.
    Unknown = 1
    # IEEE 802.3 Ethernet
    Ethernet = 6
    # IEEE 802.5 Token Ring
    TokenRing = 9
    # Fiber Distributed Data Interface
    Fddi = 15
    # ISDN Basic Rate Interface
    BasicIsdn = 20
    # ISDN Primary Rate Interface
    PrimaryIsdn = 21
    # Point-To-Point Protocol
    Ppp = 23
    # Loopback adapter
    Loopback = 24
    # Ethernet 3 Mbps (RFC 895)
    Ethernet3Megabit = 26
    # Serial Line Internet Protocol (RFC 1055)
    Slip = 28
    # Asynchronous Transfer Mode
    Atm = 37
    # Modem
    GenericModem = 48
    # Fast Ethernet 100Base-T
    FastEthernetT = 62
    # ISDN with X.25
    Isdn = 63
    # Fast Ethernet 100Base-FX
    FastEthernetFx = 69
    # IEEE 802.11 Wireless LAN
    Wireless80211 = 71
    # Asymmetric DSL
    AsymmetricDsl = 94
    # Rate Adaptive DSL
    RateAdaptDsl = 95
    # Symmetric DSL
    SymmetricDsl = 96
    # Very High Speed DSL
    VeryHighSpeedDsl = 97
    # IP over ATM
    IPOverAtm = 114
    # Gigabit Ethernet
    GigabitEthernet = 117
    # Tunnel interface
    Tunnel = 131
    # Multirate Symmetric DSL
    MultiRateSymmetricDsl = 143
    # High Performance Serial Bus
    HighPerformanceSerialBus = 144
    # WiMax (WMAN)
    Wman = 237
    # GSM-based mobile broadband
    Wwanpp = 243
    # CDMA-based mobile broadband
    Wwanpp2 = 244

@dataclass
class NetworkInterfaceInfo:
    """网络接口信息结构体"""
    name: str # 友好名称 (如 "Wi-Fi")
    description: str # 友好描述
    guid: str # GUID 名称
    if_type: int # IANA ifType
    type_string: str # 类型字符串

# 2. 定义 Windows API 结构体
if is_windows():
    class IP_ADAPTER_ADDRESSES(ctypes.Structure):
        pass

    # 定义指针以便递归引用
    PIP_ADAPTER_ADDRESSES = ctypes.POINTER(IP_ADAPTER_ADDRESSES)

    IP_ADAPTER_ADDRESSES._fields_ = [
        ("Length", wintypes.ULONG),
        ("IfIndex", wintypes.DWORD),
        ("Next", PIP_ADAPTER_ADDRESSES),
        ("AdapterName", ctypes.c_char_p),  # GUID 名称
        ("FirstUnicastAddress", ctypes.c_void_p),
        ("FirstAnycastAddress", ctypes.c_void_p),
        ("FirstMulticastAddress", ctypes.c_void_p),
        ("FirstDnsServerAddress", ctypes.c_void_p),
        ("DnsSuffix", wintypes.LPCWSTR),
        ("Description", wintypes.LPCWSTR), # 友好描述
        ("FriendlyName", wintypes.LPCWSTR),# 友好名称 (如 "Wi-Fi")
        ("PhysicalAddress", wintypes.BYTE * 8),
        ("PhysicalAddressLength", wintypes.DWORD),
        ("Flags", wintypes.DWORD),
        ("Mtu", wintypes.DWORD),
        ("IfType", wintypes.DWORD),        # <--- 这就是你要的 NetworkInterfaceType
        ("OperStatus", wintypes.DWORD),
        # 后面还有很多字段，但在 IfType 之后我们不需要定义了，
        # 只要由操作系统分配足够的内存即可。
    ]

def get_network_interface_types() -> List[NetworkInterfaceInfo]:
    """
    获取系统中所有网络接口的信息
    """
    if not is_windows():
        return []

    # 加载 iphlpapi.dll
    iphlpapi = ctypes.windll.iphlpapi
    
    # 初始缓冲区大小
    outBufLen = wintypes.ULONG(15000)
    Addresses = (ctypes.c_byte * outBufLen.value)()
    
    # 第一次调用可能会失败并返回需要的缓冲区大小，但在 Python 简单场景通常给 15k 够了
    # 这里的 Flags=0 
    ret = iphlpapi.GetAdaptersAddresses(
        0, # AF_UNSPEC
        0, # Flags
        None, 
        ctypes.byref(Addresses), 
        ctypes.byref(outBufLen)
    )
    
    if ret != 0:
        print(f"Error retrieving adapters. Error code: {ret}")
        return []

    # 遍历链表
    curr_addr = ctypes.cast(Addresses, PIP_ADAPTER_ADDRESSES)
    
    results = []
    
    while curr_addr:
        adapter = curr_addr.contents
        
        # 获取 IfType 数字
        if_type_int = adapter.IfType
        
        # 尝试映射到枚举，如果不在枚举里，保持数字
        try:
            enum_type = NetworkInterfaceType(if_type_int)
            type_str = enum_type.name
        except ValueError:
            type_str = f"Other({if_type_int})"

        info = NetworkInterfaceInfo(
            name=adapter.FriendlyName,
            description=adapter.Description,
            guid=adapter.AdapterName.decode('utf-8'),
            if_type=if_type_int,
            type_string=type_str
        )
        results.append(info)
        
        curr_addr = adapter.Next

    return results

# --- 测试代码 ---
if __name__ == "__main__":
    import os
    if os.name == 'nt': # 仅限 Windows
        interfaces = get_network_interface_types()
        for iface in interfaces:
            print(f"网卡名称: {iface.name}")
            print(f"  描述:   {iface.description}")
            print(f"  类型ID: {iface.if_type} ({iface.type_string})")
            print("-" * 30)
    else:
        print("此代码通过调用 Windows API 实现，仅支持 Windows 系统。")
