package forwarder

import (
	"albion-sniffer/sniffer"
	"fmt"
	"net"
)

type Forwarder struct {
	Targets []string
	Conn    *net.UDPConn
}

func NewForwarder(targets []string) (*Forwarder, error) {
	addr, err := net.ResolveUDPAddr("udp", ":0")
	if err != nil {
		return nil, err
	}
	conn, err := net.ListenUDP("udp", addr)
	if err != nil {
		return nil, err
	}

	return &Forwarder{
		Targets: targets,
		Conn:    conn,
	}, nil
}

func (f *Forwarder) Start(input <-chan sniffer.Packet) {
	go func() {
		for p := range input {
			f.send(p.Payload)
		}
	}()
}

func (f *Forwarder) send(data []byte) {
	for _, target := range f.Targets {
		addr, err := net.ResolveUDPAddr("udp", target)
		if err != nil {
			fmt.Printf("Error resolving target %s: %v\n", target, err)
			continue
		}
		_, err = f.Conn.WriteToUDP(data, addr)
		if err != nil {
			fmt.Printf("Error sending to %s: %v\n", target, err)
		}
	}
}
