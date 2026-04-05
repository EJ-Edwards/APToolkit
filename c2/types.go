package c2

// Task represents a command to be executed by an implant.
type Task struct {
	ID      string `json:"id"`
	Command string `json:"command"`
}

// Result represents the output of a task.
type Result struct {
	TaskID string `json:"task_id"`
	Output string `json:"output"`
}
