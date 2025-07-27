package main

import (
	"log"
	"net/http"
	"github.com/pion/ion-sfu/pkg/sfu"
	"github.com/pion/webrtc/v3"
	"github.com/pion/ion-sfu/pkg/signal/ws"
)

func main() {
	cfg := sfu.Config{}
	s := sfu.NewSFU(cfg)
	
	// Optional: Configure bandwidth estimation, Simulcast etc.
	api := sfu.NewAPI(sfu.WithMediaEngine(&webrtc.MediaEngine{}))
	handler := ws.NewSignalHandler(s, api)
	http.HandleFunc("/ws", handler.ServeHTTP)

	log.Println("SFU server started on :7000")
	err := http.ListenAndServe(":7000", nil)
	if err != nil {
		panic(err)
	}
}