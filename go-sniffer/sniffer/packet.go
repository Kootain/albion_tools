package sniffer

type Packet struct {
	Device  string
	Payload []byte
	SrcPort int
	DstPort int
}
