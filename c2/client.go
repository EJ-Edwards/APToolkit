package c2

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

// C2Client is used by the operator to manage the C2.
type C2Client struct {
	BaseURL    string
	HTTPClient *http.Client
}

// NewOperatorClient creates a new client.
func NewOperatorClient(serverURL string) *C2Client {
	return &C2Client{
		BaseURL:    serverURL,
		HTTPClient: &http.Client{},
	}
}

// AddTask sends a command to the server.
func (c *C2Client) AddTask(taskID, command string) error {
	task := Task{ID: taskID, Command: command}
	taskJSON, err := json.Marshal(task)
	if err != nil {
		return fmt.Errorf("failed to marshal task: %w", err)
	}

	url := c.BaseURL + "/addtask"
	resp, err := c.HTTPClient.Post(url, "application/json", bytes.NewBuffer(taskJSON))
	if err != nil {
		return fmt.Errorf("failed to send task: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("server returned %s", resp.Status)
	}

	fmt.Printf("[+] Task '%s' sent successfully.\n", command)
	return nil
}

// GetResults fetches all results from the server.
func (c *C2Client) GetResults() (map[string]Result, error) {
	url := c.BaseURL + "/getresults"
	resp, err := c.HTTPClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to get results: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("server returned %s", resp.Status)
	}

	var results map[string]Result // Corrected from Map to map
	if err := json.NewDecoder(resp.Body).Decode(&results); err != nil {
		return nil, fmt.Errorf("failed to decode results: %w", err)
	}
	return results, nil
}
