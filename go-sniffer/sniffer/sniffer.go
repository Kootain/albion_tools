package sniffer

import (
	"albion-sniffer/photon"
	"fmt"
	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcap"
)

type Sniffer struct {
	DeviceName string
	Handle     *pcap.Handle
	Output     chan<- Packet
	StopChan   chan struct{}
}

func NewSniffer(device string, output chan<- Packet) *Sniffer {
	return &Sniffer{
		DeviceName: device,
		Output:     output,
		StopChan:   make(chan struct{}),
	}
}

func (s *Sniffer) Start(ports []int) error {
	handle, err := pcap.OpenLive(s.DeviceName, 65536, true, pcap.BlockForever)
	if err != nil {
		return err
	}
	s.Handle = handle

	// BPF Filter
	// Filter UDP ports AND exclude local traffic to self (prevent loops if listening on localhost)
	filter := "("
	for i, port := range ports {
		if i > 0 {
			filter += " or "
		}
		filter += fmt.Sprintf("udp port %d", port)
	}
	filter += ")"
	
	if filter != "()" {
		if err := handle.SetBPFFilter(filter); err != nil {
			handle.Close()
			return err
		}
	}

	go s.run()
	return nil
}

func (s *Sniffer) Stop() {
	close(s.StopChan)
	if s.Handle != nil {
		s.Handle.Close()
	}
}

func (s *Sniffer) run() {
	source := gopacket.NewPacketSource(s.Handle, s.Handle.LinkType())
	
	packetChan := source.Packets()

	for {
		select {
		case <-s.StopChan:
			return
		case packet, ok := <-packetChan:
			if !ok {
				return
			}
            
			udpLayer := packet.Layer(layers.LayerTypeUDP)
			if udpLayer == nil {
				continue
			}
			udp, _ := udpLayer.(*layers.UDP)
            
            payload := udp.Payload
            if len(payload) == 0 {
                continue
            }

            // Check Photon
            if !photon.IsPhotonPacket(int(udp.SrcPort), int(udp.DstPort), payload) {
                continue
            }

			s.Output <- Packet{
				Device:  s.DeviceName,
				Payload: payload,
                SrcPort: int(udp.SrcPort),
                DstPort: int(udp.DstPort),
			}
		}
	}
}
