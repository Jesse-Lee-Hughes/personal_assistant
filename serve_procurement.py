from __future__ import annotations

import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent
DATA_FILE = ROOT_DIR / "files" / "motorcycle_procurement.json"

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>Motorcycle Procurement Results</title>
    <style>
        :root {
            font-family: Arial, sans-serif;
            background: #f6f6f6;
            color: #222;
        }
        body {
            margin: 0;
            padding: 2rem;
        }
        header {
            margin-bottom: 1.5rem;
        }
        h1 {
            margin: 0;
            font-size: 1.75rem;
        }
        #status {
            margin-top: 0.5rem;
            color: #555;
        }
        pre {
            background: #fff;
            border: 1px solid #ddd;
            padding: 1rem;
            overflow-x: auto;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        button {
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
            border-radius: 4px;
            border: 1px solid #2a73cc;
            background: #2d7ff9;
            color: #fff;
            cursor: pointer;
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <header>
        <h1>Motorcycle Procurement Results</h1>
        <p id="status">Loading latest report…</p>
        <button id="refresh">Refresh</button>
    </header>
    <pre id="payload">{}</pre>

    <script>
        const status = document.getElementById("status");
        const payload = document.getElementById("payload");
        const refreshBtn = document.getElementById("refresh");

        async function fetchReport() {
            status.textContent = "Loading latest report…";
            refreshBtn.disabled = true;
            try {
                const response = await fetch("/api/procurement", {
                    headers: {"Accept": "application/json"}
                });
                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}`);
                }
                const data = await response.json();
                status.textContent = data.meta.message;
                payload.textContent = JSON.stringify(data.payload, null, 2);
            } catch (err) {
                status.textContent = err.message || "Failed to load report.";
                payload.textContent = "";
            } finally {
                refreshBtn.disabled = false;
            }
        }

        refreshBtn.addEventListener("click", fetchReport);
        fetchReport();
    </script>
</body>
</html>
""".strip()


class ProcurementHandler(BaseHTTPRequestHandler):
    server_version = "ProcurementHTTP/1.0"

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._serve_index()
        elif self.path == "/api/procurement":
            self._serve_procurement()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, format: str, *args: Any) -> None:
        logging.info("%s - %s", self.address_string(), format % args)

    def _serve_index(self) -> None:
        body = INDEX_HTML.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_procurement(self) -> None:
        payload, message, status = self._read_procurement()
        body = json.dumps({"meta": {"message": message}, "payload": payload}).encode(
            "utf-8"
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_procurement(self) -> tuple[Dict[str, Any], str, int]:
        if not DATA_FILE.exists():
            return {}, "Report not found. Run the procurement agent to generate results.", HTTPStatus.NOT_FOUND
        try:
            with DATA_FILE.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError:
            text = DATA_FILE.read_text(encoding="utf-8")
            return (
                {"raw_text": text},
                "Latest report is not valid JSON; showing raw content.",
                HTTPStatus.OK,
            )
        return data, "Loaded report from motorcycle_procurement.json.", HTTPStatus.OK


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    address = (host, port)
    httpd = HTTPServer(address, ProcurementHandler)
    logging.info("Serving procurement viewer at http://%s:%s", host, port)
    logging.info("Data file: %s", DATA_FILE)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down server.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
