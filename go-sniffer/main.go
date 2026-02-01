package main

import (
	"albion-sniffer/config"
	"albion-sniffer/forwarder"
	"albion-sniffer/sniffer"
	systray_pkg "albion-sniffer/systray"
	_ "embed"
	"fmt"
	"github.com/getlantern/systray"
)

//go:embed config.json
var defaultConfig []byte

func main() {
	cfg, err := config.LoadWithFallback("config.json", defaultConfig)
	if err != nil {
		fmt.Printf("Failed to load config: %v\n", err)
		return
	}

	manager := sniffer.NewManager(cfg)

	// Start Sniffer
	go func() {
		if err := manager.Start(); err != nil {
			fmt.Printf("Manager start failed: %v\n", err)
		}
	}()

	// Start Forwarder
	fwd, err := forwarder.NewForwarder(cfg.Targets)
	if err != nil {
		fmt.Printf("Forwarder init failed: %v\n", err)
		return
	}

	packetChan := manager.GetPacketChannel()
	fwd.Start(packetChan)

	// UI
	u := &systray_pkg.UI{Manager: manager}
	systray.Run(u.OnReady, u.OnExit)
}
