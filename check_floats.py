
import struct

# Data from log
data = bytes.fromhex("032872f172a85cde0898a8b6818913e2dcfa6666f64012a59781026debdc")

data = b'\x01lJG\r\xd6\\\xde\x08?v\x913\xca#\x0c\xe8\x11\x00\x00\xb0@'

print(f"Data length: {len(data)}")

def unpack_floats():
    # Proposed structure:
    # 0: B
    # 1: Q
    # 9: f (X1)
    # 13: f (Y1)
    # 17: B (Angle)
    # 18: f (Speed)
    # 22: f (X2)
    # 26: f (Y2)
    
    flag = data[0]
    print(f"Flag: {flag}")

    timestamp = struct.unpack_from('<Q', data, 1)[0]
    print(f"Timestamp: {timestamp}")

    x1 = struct.unpack_from('<f', data, 9)[0]
    y1 = struct.unpack_from('<f', data, 13)[0]
    print(f"Pos 1: ({x1}, {y1})")

    angle = data[17]
    print(f"Angle: {angle}")

    speed = struct.unpack_from('<f', data, 18)[0]
    print(f"Speed: {speed}")

    x2 = struct.unpack_from('<f', data, 22)[0]
    y2 = struct.unpack_from('<f', data, 26)[0]
    print(f"Pos 2: ({x2}, {y2})")

unpack_floats()
