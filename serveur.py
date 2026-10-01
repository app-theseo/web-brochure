"""Serveur local pour la brochure : python serveur.py  ->  http://localhost:8765
Sert index.html et fournit /proxy (page web), /img (images) et /pdf (export, si Chrome/Chromium est installé)."""
import http.server, os, shutil, subprocess, tempfile, urllib.parse, urllib.request

PORT = 8765
HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (compatible; BrochureMVP/1.0)"}


def find_chrome():
    for n in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        p = shutil.which(n)
        if p:
            return p
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if os.path.exists(p):
            return p


class H(http.server.BaseHTTPRequestHandler):
    def send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def fetch(self, url):
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL invalide")
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            return r.read(), r.headers.get("Content-Type", "application/octet-stream"), r.headers.get_content_charset()

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                with open(os.path.join(HERE, "index.html"), "rb") as f:
                    return self.send(200, f.read(), "text/html; charset=utf-8")
            if u.path == "/proxy":
                data, _, cs = self.fetch(q["url"][0])
                return self.send(200, data.decode(cs or "utf-8", "replace").encode("utf-8"), "text/html; charset=utf-8")
            if u.path == "/img":
                data, ct, _ = self.fetch(q["url"][0])
                return self.send(200, data, ct)
            self.send(404, b"not found")
        except Exception as e:
            self.send(502, str(e).encode())

    def do_POST(self):
        if self.path != "/pdf":
            return self.send(404, b"not found")
        chrome = find_chrome()
        if not chrome:
            return self.send(501, b"Chrome/Chromium introuvable")
        html = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        with tempfile.TemporaryDirectory() as d:
            src, out = os.path.join(d, "b.html"), os.path.join(d, "b.pdf")
            with open(src, "wb") as f:
                f.write(html)
            try:
                subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                                "--print-to-pdf=" + out, "file://" + src.replace("\\", "/") if os.name != "nt" else "file:///" + src.replace("\\", "/")],
                               check=True, timeout=60, capture_output=True)
                with open(out, "rb") as f:
                    self.send(200, f.read(), "application/pdf")
            except Exception as e:
                self.send(500, str(e).encode())


if __name__ == "__main__":
    print(f"Brochure : http://localhost:{PORT}  (Ctrl+C pour arrêter)")
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
