package photon

var (
	UDPPorts   = map[int]bool{5055: true, 5056: true, 5058: true}
	MagicBytes = map[byte]bool{0xF1: true, 0xF2: true, 0xFE: true}
	MinPayloadLength = 3
)
