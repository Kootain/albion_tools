
import struct
import time

# The byte string from the log
data = b'\x03(r\xf1r\xa8\\\xde\x08\x98\xa8\xb6\x81\x89\x13\xe2\xdc\xfaff\xf6@\x12\xa5\x97\x81\x02m\xeb\xdc'

print(f"Total Length: {len(data)}")

# Helper to print floats
def try_unpack(fmt, offset=0):
    try:
        size = struct.calcsize(fmt)
        if offset + size > len(data):
            return
        val = struct.unpack_from(fmt, data, offset)
        print(f"Format '{fmt}' at {offset}: {val}")
    except Exception as e:
        print(f"Error {fmt}: {e}")

# Albion positions are usually floats (4 bytes)
# Timestamps might be long (8 bytes) or int (4 bytes)
# Let's try to find sensible float values (coordinates usually -1000 to 1000, or larger if global coords)
# Albion coordinates: (X, Y) usually. Z is height (often 0 or small).
# Sometimes packed as (X, Y) or (X, Z, Y)

print("--- Trying to find floats ---")
for i in range(len(data) - 4 + 1):
    try_unpack('<f', i)

print("\n--- Trying to find ints ---")
for i in range(len(data) - 4 + 1):
    try_unpack('<I', i)

print("\n--- Trying to find longs ---")
for i in range(len(data) - 8 + 1):
    try_unpack('<Q', i)
    
print("\n--- Bytes Hex ---")
print(data.hex())
