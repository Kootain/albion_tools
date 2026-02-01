package sniffer

import (
	"albion-sniffer/config"
	"fmt"
	"sync"
	"time"
)

type Manager struct {
	Config       *config.Config
	Sniffers     map[string]*Sniffer
	PacketChan   chan Packet
	ActiveDevice string
	DeviceScores map[string]int
	LastValid    time.Time
	mu           sync.Mutex
}

func NewManager(cfg *config.Config) *Manager {
	return &Manager{
		Config:       cfg,
		Sniffers:     make(map[string]*Sniffer),
		PacketChan:   make(chan Packet, 1000),
		DeviceScores: make(map[string]int),
	}
}

func (m *Manager) Start() error {
	devices, err := GetDevices()
	if err != nil {
		return err
	}

	for _, dev := range devices {
		// Filter out Loopback and inactive devices to avoid false positives
		// pcap.Interface struct in older gopacket versions might not have Loopback field directly or it's named differently?
		// Checking flags if available or just relying on Addresses length.
        // Actually, gopacket's Interface struct has a Flags field, and pcap.IF_LOOPBACK check is needed.
        // But simply checking address length is a good heuristic for now.
		if len(dev.Addresses) == 0 {
			continue
		}
        
        // Check for loopback by name or description as a fallback if field missing
        if dev.Name == "\\Device\\NPF_Loopback" || dev.Description == "Loopback" {
             continue
        }
		
		s := NewSniffer(dev.Name, m.PacketChan)
		if err := s.Start(m.Config.Ports); err != nil {
			// Don't fail completely, just log
			fmt.Printf("Warning: Failed to start sniffer on %s: %v\n", dev.Name, err)
			continue
		}
		m.Sniffers[dev.Name] = s
		fmt.Printf("Started sniffer on %s (%s)\n", dev.Name, dev.Description)
	}
    
    if len(m.Sniffers) == 0 {
        return fmt.Errorf("no devices opened")
    }

	return nil
}

func (m *Manager) Stop() {
	for _, s := range m.Sniffers {
		s.Stop()
	}
}

func (m *Manager) GetPacketChannel() <-chan Packet {
    out := make(chan Packet, 1000)
    go func() {
        for p := range m.PacketChan {
            if m.updateLock(p.Device) {
                out <- p
            }
        }
    }()
    return out
}

func (m *Manager) updateLock(device string) bool {
	m.mu.Lock()
	defer m.mu.Unlock()

	now := time.Now()
    // Timeout
	if m.ActiveDevice != "" && now.Sub(m.LastValid) > time.Duration(m.Config.LockTimeout)*time.Second {
		fmt.Println("Device lock timed out")
		m.ActiveDevice = ""
		m.DeviceScores = make(map[string]int)
	}

	if m.ActiveDevice != "" && m.ActiveDevice != device {
		return false
	}

	m.DeviceScores[device]++
	if m.DeviceScores[device] >= m.Config.LockScore {
		if m.ActiveDevice == "" {
			m.ActiveDevice = device
			fmt.Printf("Locked to device: %s\n", device)
		}
		m.LastValid = now
		return true
	}
    
    return m.ActiveDevice == "" || m.ActiveDevice == device
}

func (m *Manager) GetActiveDeviceName() string {
    m.mu.Lock()
    defer m.mu.Unlock()
    if m.ActiveDevice == "" {
        return "None"
    }
    return m.ActiveDevice
}
