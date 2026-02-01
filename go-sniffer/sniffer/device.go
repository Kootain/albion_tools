package sniffer

import (
	"fmt"
	"github.com/google/gopacket/pcap"
)

func GetDevices() ([]pcap.Interface, error) {
	devices, err := pcap.FindAllDevs()
	if err != nil {
		return nil, err
	}
	if len(devices) == 0 {
		return nil, fmt.Errorf("no devices found")
	}
	return devices, nil
}
