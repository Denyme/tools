import asyncio
import h2.connection
import h2.events
import socket
import ssl

async def send_http2_request(host, port, path="/", num_requests=100):
    # Создаем SSL контекст
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Создаем TCP-соединение и оборачиваем его в SSL
    sock = socket.create_connection((host, port))
    ssl_sock = ssl_context.wrap_socket(sock, server_hostname=host)

    conn = h2.connection.H2Connection()

    # Инициализация HTTP/2 соединения
    conn.initiate_connection()
    ssl_sock.sendall(conn.data_to_send())

    # Отправка запросов
    for i in range(num_requests):
        stream_id = conn.get_next_available_stream_id()  # Новый стрим для каждого запроса
        headers = [
            (':method', 'GET'),
            (':path', path),
            (':authority', host),
            (':scheme', 'https'),
        ]
        conn.send_headers(stream_id, headers, end_stream=False)
        ssl_sock.sendall(conn.data_to_send())

        # Ожидаем ответа от сервера
        while True:
            data = ssl_sock.recv(65535)
            if not data:
                break
            events = conn.receive_data(data)
            for event in events:
                if isinstance(event, h2.events.ResponseReceived):
                    print(f"Response received for stream {event.stream_id}, request {i + 1}")
                    break
            ssl_sock.sendall(conn.data_to_send())
            break  # Переходим к следующему запросу после получения ответа

    ssl_sock.close()

if __name__ == "__main__":
    # Запуск нагрузочного теста
    asyncio.run(send_http2_request(
        "server_name or IP",
        12000,
        "/",
        num_requests=200
    ))
