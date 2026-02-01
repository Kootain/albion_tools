import uuid

def object_to_guid(value) -> uuid.UUID | None:
    """
    模拟C#的ObjectToGuid方法：尝试将对象转换为UUID（Guid）
    :param value: 任意输入对象
    :return: 成功则返回uuid.UUID对象，失败/不满足条件返回None
    """
    try:
        # 1. 判断是否为可迭代对象（对应C#的IEnumerable）
        # 尝试将value转为迭代器，非可迭代对象会抛出TypeError
        iter(value)
        
        # 2. 过滤出字节类型的元素（C# OfType<byte>()）
        # Python中字节用0-255的int表示，需校验范围
        byte_list = []
        for elem in value:
            # 校验元素是整数且在字节范围内（0-255）
            if isinstance(elem, int) and 0 <= elem <= 255:
                byte_list.append(elem)
        
        # 3. 转换为bytes数组（需16个字节才能创建UUID）
        byte_array = bytes(byte_list)
        if len(byte_array) != 16:
            # UUID需要恰好16个字节，否则创建失败
            return None
        
        # 4. 用字节数组创建UUID（对应C# new Guid(myBytes)）
        return uuid.UUID(bytes=byte_array)
    
    except (TypeError, ValueError, AttributeError):
        # 捕获所有可能的异常：非可迭代、字节数不足、创建UUID失败等
        return None

def to_int(x):
    try:
        if isinstance(x, (bytes, bytearray)):
            return int.from_bytes(x, byteorder="little", signed=False)
        return int(x)
    except Exception:
        return 0

def to_str(x):
    try:
        return str(x) if x is not None else ""
    except Exception:
        return ""

def to_int_list(x):
    if x is None:
        return []
    if isinstance(x, (bytes, bytearray)):
        return list(x)
    if isinstance(x, (list, tuple)):
        try:
            return [int(i) for i in x]
        except Exception:
            return []
    return []


# ------------------- 测试案例 -------------------
if __name__ == "__main__":
    # 测试1：有效字节数组（16个字节）→ 返回UUID
    valid_bytes = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                   0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10]
    guid1 = object_to_guid(valid_bytes)
    print("测试1（有效字节数组）:", guid1)  # 输出类似：04030201-0605-0807-090a-0b0c0d0e0f10

    # 测试2：非可迭代对象（整数）→ 返回None
    guid2 = object_to_guid(123)
    print("测试2（非可迭代对象）:", guid2)  # 输出：None

    # 测试3：可迭代但字节数不足 → 返回None
    invalid_bytes = [1, 2, 3]
    guid3 = object_to_guid(invalid_bytes)
    print("测试3（字节数不足）:", guid3)  # 输出：None

    # 测试4：可迭代但包含非字节元素 → 过滤后字节数不足，返回None
    mixed_list = [1, 2, "3", 4]
    guid4 = object_to_guid(mixed_list)
    print("测试4（含非字节元素）:", guid4)  # 输出：None