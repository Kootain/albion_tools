package config

import (
	"encoding/json"
	"os"
)

type Config struct {
	Targets     []string `json:"targets"`
	Ports       []int    `json:"ports"`
	LockScore   int      `json:"lock_score"`
	LockTimeout int      `json:"lock_timeout"`
}

func Load(path string) (*Config, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var cfg Config
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}

func LoadFromBytes(data []byte) (*Config, error) {
	var cfg Config
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}

func LoadWithFallback(path string, fallback []byte) (*Config, error) {
    // Try to load from file first
    cfg, err := Load(path)
    if err == nil {
        return cfg, nil
    }
    
    // If file doesn't exist (or other error), try fallback
    return LoadFromBytes(fallback)
}
