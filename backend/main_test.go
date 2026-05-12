package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func TestDefaultConfigIsLocalAndCorsRestricted(t *testing.T) {
	t.Setenv("GOPRAC_BIND_ADDR", "")
	t.Setenv("GOPRAC_ALLOWED_ORIGINS", "")

	cfg := loadConfig()
	if cfg.BindAddr != "127.0.0.1" {
		t.Fatalf("default bind address = %q, want 127.0.0.1", cfg.BindAddr)
	}
	if _, ok := cfg.AllowedOrigins["*"]; ok {
		t.Fatal("wildcard origin should never be allowed")
	}
	if _, ok := cfg.AllowedOrigins["http://localhost:5173"]; !ok {
		t.Fatal("default localhost frontend origin missing")
	}
}

func TestCorsRejectsUnknownOrigin(t *testing.T) {
	config = Config{AllowedOrigins: parseOrigins("http://localhost:5173")}
	handler := cors(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNoContent)
	})

	req := httptest.NewRequest(http.MethodPost, "/api/run", nil)
	req.Header.Set("Origin", "https://example.test")
	rr := httptest.NewRecorder()

	handler(rr, req)

	if rr.Code != http.StatusForbidden {
		t.Fatalf("status = %d, want %d", rr.Code, http.StatusForbidden)
	}
}

func TestRunCodeRejectsOversizedBody(t *testing.T) {
	config = Config{MaxBodyBytes: 16, MaxCodeBytes: 1024, RunTimeout: time.Second}
	runSlots = make(chan struct{}, 1)
	store = Store{Problems: []Problem{{ID: "hello"}}}

	req := httptest.NewRequest(http.MethodPost, "/api/run", strings.NewReader(`{"problemId":"hello","code":"package main"}`))
	rr := httptest.NewRecorder()

	runCode(rr, req)

	if rr.Code != http.StatusRequestEntityTooLarge {
		t.Fatalf("status = %d, want %d", rr.Code, http.StatusRequestEntityTooLarge)
	}
}

func TestRunCodeLimitsConcurrentRuns(t *testing.T) {
	config = Config{MaxBodyBytes: 1024, MaxCodeBytes: 1024, RunTimeout: time.Second}
	runSlots = make(chan struct{}, 1)
	runSlots <- struct{}{}
	store = Store{Problems: []Problem{{ID: "hello"}}}

	req := httptest.NewRequest(http.MethodPost, "/api/run", strings.NewReader(`{"problemId":"hello","code":"package main","mode":"run"}`))
	rr := httptest.NewRecorder()

	runCode(rr, req)

	if rr.Code != http.StatusTooManyRequests {
		t.Fatalf("status = %d, want %d", rr.Code, http.StatusTooManyRequests)
	}
}
