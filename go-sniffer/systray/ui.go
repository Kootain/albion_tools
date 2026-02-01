package ui

import (
	"albion-sniffer/sniffer"
	"fmt"
	"github.com/getlantern/systray"
	"time"
)

type UI struct {
	Manager *sniffer.Manager
}

func (u *UI) OnReady() {
	systray.SetIcon(IconOffline)
	systray.SetTitle("Albion Sniffer")
	systray.SetTooltip("Albion Online Sniffer")

	mStatus := systray.AddMenuItem("Status: Idle", "Sniffer Status")
    mStatus.Disable() // Just a label for now
	mDevice := systray.AddMenuItem("Device: Scanning...", "Active Device")
	systray.AddSeparator()
	mQuit := systray.AddMenuItem("Quit", "Quit the application")

	go func() {
        lastState := false
		for {
			dev := u.Manager.GetActiveDeviceName()
            isLocked := dev != "None"
            
			mDevice.SetTitle(fmt.Sprintf("Device: %s", dev))
            
            if isLocked != lastState {
                if isLocked {
                    systray.SetIcon(IconOnline)
                    mStatus.SetTitle("Status: Locked")
                } else {
                    systray.SetIcon(IconOffline)
                    mStatus.SetTitle("Status: Idle")
                }
                lastState = isLocked
            }
            
			time.Sleep(1 * time.Second)
		}
	}()

	go func() {
		<-mQuit.ClickedCh
		systray.Quit()
	}()
}

func (u *UI) OnExit() {
	u.Manager.Stop()
}
