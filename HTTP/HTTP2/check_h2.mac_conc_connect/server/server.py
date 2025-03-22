from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Отправляем ответ с кодом 200 и простым текстом
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello from mock server!")

    def do_POST(self):
        # Обработка POST-запросов (если нужно)
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"POST request received: " + body)

# Настройка HTTPS (если требуется)
httpd = HTTPServer(('0.0.0.0', 443), SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(
    httpd.socket,
    keyfile="",  # Путь к ключу
    certfile="",  # Путь к сертификату
    server_side=True
)

print("Mock server is running on https://0.0.0.0:443")
httpd.serve_forever()
