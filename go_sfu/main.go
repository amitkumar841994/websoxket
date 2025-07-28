package main

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/pion/ion-sfu/pkg/sfu"
	"github.com/pion/webrtc/v3"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func main() {
	// Step 1: Create SFU instance
	sfuCfg := sfu.Config{}
	s := sfu.NewSFU(sfuCfg)

	// Step 2: Set up Gin router
	r := gin.Default()

	r.GET("/ws", func(c *gin.Context) {
		conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			log.Println("WebSocket upgrade failed:", err)
			return
		}
		defer conn.Close()

		// Step 3: Receive offer from WebSocket client
		_, msg, err := conn.ReadMessage()
		if err != nil {
			log.Println("Failed to read message:", err)
			return
		}

		var offer webrtc.SessionDescription
		if err := json.Unmarshal(msg, &offer); err != nil {
			log.Println("Invalid SDP:", err)
			return
		}

		// Step 4: Create peer connection
		peer := s.NewPeer(nil) // No custom API
		if err := peer.SetRemoteDescription(offer); err != nil {
			log.Println("SetRemoteDescription failed:", err)
			return
		}

		answer, err := peer.CreateAnswer()
		if err != nil {
			log.Println("CreateAnswer failed:", err)
			return
		}

		if err := peer.SetLocalDescription(answer); err != nil {
			log.Println("SetLocalDescription failed:", err)
			return
		}

		// Step 5: Send answer back over WebSocket
		answerJSON, _ := json.Marshal(answer)
		if err := conn.WriteMessage(websocket.TextMessage, answerJSON); err != nil {
			log.Println("WriteMessage failed:", err)
			return
		}
	})

	log.Println("SFU signaling server running at :7000")
	r.Run(":7000")
}
