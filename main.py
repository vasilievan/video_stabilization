from http.server import HTTPServer
from server.server import Server
import os

if __name__ == "__main__":
    if not os.path.exists("server/stabilized"):
        os.mkdir("server/stabilized")
    if not os.path.exists("server/unstabilized"):
        os.mkdir("server/unstabilized")
    env_port = os.getenv("PORT")
    if env_port is None:
        port = 8080
    else:
        port = int(env_port)
    hostname = "0.0.0.0"
    server = HTTPServer((hostname, port), Server)
    print("Server started http://%s:%s" % (hostname, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print("Server stopped.")
