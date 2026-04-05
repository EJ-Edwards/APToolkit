package c2

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"c2" // Import the module we just created
)

func main() {
	// 1. Initialize the C2 server logic
	c2Server := c2.NewC2Server()

	// 2. Create the HTTP server wrapper
	httpServer := c2.NewServer(":8080", c2Server)

	// 3. Start the server in a goroutine to allow for graceful shutdown
	go c2.StartServer(httpServer)

	log.Println("[+] C2 Server is running. Press Ctrl+C to stop.")

	// 4. Wait for an interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("[-] Shutting down server...")

	if err := httpServer.Close(); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	log.Println("[-] Server exited.")
}
