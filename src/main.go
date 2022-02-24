package main

import (
	"bufio"
	"fmt"
	"net/http"
)

func handler(w http.ResponseWriter, req *http.Request) {
	// Request AWS metadata for Availability zone
	az_endpoint := "http://169.254.169.254/latest/meta-data/placement/availability-zone"
	resp, err := http.Get(az_endpoint)
	if err != nil {
		fmt.Fprintf(w, "I could not reach meta-data endpoint!")
	} else {
		defer resp.Body.Close()
		scanner := bufio.NewScanner(resp.Body)
		for i := 0; scanner.Scan(); i++ {
			fmt.Fprintf(w, scanner.Text())
		}

	}
}

func main() {
	http.HandleFunc("/", handler)
	http.ListenAndServe(":8080", nil)
}
