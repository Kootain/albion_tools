package photon

func IsPhotonPacket(srcPort, dstPort int, payload []byte) bool {
	if len(payload) < MinPayloadLength {
		return false
	}

	portMatch := UDPPorts[srcPort] || UDPPorts[dstPort]
	signatureMatch := MagicBytes[payload[0]]

	return portMatch || signatureMatch
}
