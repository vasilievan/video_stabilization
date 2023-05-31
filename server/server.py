import cgi
import threading
from http.server import BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import random
from stabilization import Stabilization


class Server(BaseHTTPRequestHandler):
    blue_blue_sky = "blue_blue_sky.png"
    door = "indoor"
    favicon = "favicon.ico"
    hide_script = "hide_script.js"
    index = "index.html"
    index_script = "index_script.js"
    not_found = "not_found.html"
    not_found_script = "not_found_script.js"
    not_yet = "not_yet.html"
    not_yet_script = "not_yet_script.js"
    ready_to_serve = {}
    server = "server/"
    stabilization = "stabilization.html"
    stabilized = "stabilized.mp4"
    styles = "styles.css"
    rb = "rb"
    root = "/"

    with open(server + blue_blue_sky, rb) as file:
        blue_blue_sky_file: bytes = file.read()
        file.close()
    with open(server + favicon, rb) as file:
        favicon_file: bytes = file.read()
        file.close()
    with open(server + index, rb) as file:
        index_file: bytes = file.read()
        file.close()
    with open(server + index_script, rb) as file:
        index_script_file: bytes = file.read()
        file.close()
    with open(server + not_found, rb) as file:
        not_found_file: bytes = file.read().rstrip()
        file.close()
    with open(server + not_found_script, rb) as file:
        not_found_script_file: bytes = file.read()
        file.close()
    with open(server + not_yet, rb) as file:
        not_yet_file: bytes = file.read()
        file.close()
    with open(server + not_yet_script, rb) as file:
        not_yet_script_file: bytes = file.read()
        file.close()
    with open(server + stabilization, rb) as file:
        stabilization_file: bytes = file.read()
        file.close()
    with open(server + styles, rb) as file:
        styles_file: bytes = file.read()
        file.close()
    with open(server + hide_script, rb) as file:
        hide_script_file: bytes = file.read()
        file.close()

    def handle_get(self):
        if self.path == self.root:
            self.handle_get_index()
        elif self.path.endswith(self.blue_blue_sky):
            self.handle_get_blue_blue_sky()
        elif self.path.endswith(self.favicon):
            self.handle_get_favicon()
        elif self.path.endswith(self.hide_script):
            self.handle_get_hide_script()
        elif self.path.endswith(self.index_script):
            self.handle_get_index_script()
        elif self.path.endswith(self.not_found_script):
            self.handle_get_not_found_script()
        elif self.path.endswith(self.not_yet):
            self.handle_get_not_yet()
        elif self.path.endswith(self.not_yet_script):
            self.handle_get_not_yet_script()
        elif self.path.endswith(self.stabilization):
            self.handle_get_stabilization()
        elif self.path.endswith(self.stabilized):
            self.handle_get_stabilized()
        elif self.path.endswith(self.styles):
            self.handle_get_styles()
        else:
            self.handle_get_not_found()

    def handle_get_index(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(self.index_file)

    def handle_get_blue_blue_sky(self):
        self.send_response(200)
        self.send_header("Content-type", "image/png")
        self.end_headers()
        self.wfile.write(self.blue_blue_sky_file)

    def handle_get_favicon(self):
        self.send_response(200)
        self.send_header("Content-type", "image/x-icon")
        self.end_headers()
        self.wfile.write(self.favicon_file)

    def handle_get_hide_script(self):
        self.send_response(200)
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        self.wfile.write(self.hide_script_file)

    def handle_get_index_script(self):
        self.send_response(200)
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        self.wfile.write(self.index_script_file)

    def handle_get_not_found_script(self):
        self.send_response(200)
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        self.wfile.write(self.not_found_script_file)

    def handle_get_not_yet(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(self.not_yet_file)

    def handle_get_not_yet_script(self):
        self.send_response(200)
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        self.wfile.write(self.not_yet_script_file)

    def handle_get_stabilization(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(self.stabilization_file)

    def handle_get_stabilized(self):
        self.send_response(200)
        cookie = SimpleCookie(self.headers.get("Cookie"))
        session_id = cookie["session-id"].value
        if session_id in self.ready_to_serve:
            if self.ready_to_serve[session_id]:
                to_load = 'server/stabilized/stabilized_%s.mp4' % session_id
                self.send_header("Content-type", "application/force-download")
                self.send_header("Content-Transfer-Encoding", "binary")
                self.send_header("Content-Disposition", "attachment; filename=stabilized.mp4")
                self.end_headers()
                with open(to_load, 'rb') as file:
                    self.wfile.write(file.read())
                    file.close()
            else:
                self.handle_get_not_yet()
        else:
            self.handle_get_not_found()

    def handle_get_styles(self):
        self.send_response(200)
        self.send_header("Content-type", "text/css")
        self.end_headers()
        self.wfile.write(self.styles_file)

    def handle_get_not_found(self):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(self.not_found_file)

    def handle_get_stabilize(self):
        self.send_response(200)
        cookie = SimpleCookie()
        session_id = str(random.randint(0, 4294967295))
        cookie['session-id'] = session_id
        self.ready_to_serve[session_id] = False
        self.send_header("Content-type", "text/html")
        for morsel in cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())
        self.end_headers()
        self.wfile.write(self.stabilization_file)
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, pdict)
            neural_or_not = fields['feature'][0]
            if 'door' in fields:
                this_door = fields['door'][0]
            else:
                this_door = 'door'
            self.door = str(this_door)
            raw_bytes = fields['upload-video'][0]
            to_save = 'server/unstabilized/to_stabilize_%s.mp4' % session_id
            to_load = 'server/stabilized/stabilized_%s.mp4' % session_id
            with open(to_save, 'wb') as file:
                file.write(raw_bytes)
                file.close()
            return neural_or_not, session_id, to_save, to_load
        return None

    def stabilize_video_neural(self, to_stabilize: str, stabilized: str, door: str, session_id: str):
        stabilization = Stabilization(to_stabilize, stabilized, door=door)
        stabilization.stabilize_video_neural()
        self.ready_to_serve[session_id] = True

    def stabilize_video_standard(self, to_stabilize: str, stabilized: str, session_id: str):
        stabilization = Stabilization(to_stabilize, stabilized)
        stabilization.stabilize_video_standard()
        self.ready_to_serve[session_id] = True

    def do_GET(self):
        self.handle_get()

    def do_POST(self):
        if self.path == "/stabilize":
            neural_or_not, session_id, to_stabilize, stabilized = self.handle_get_stabilize()
            if neural_or_not == "neural":
                thread = threading.Thread(target=self.stabilize_video_neural,
                                          args=[to_stabilize, stabilized, self.door, session_id])
                thread.start()
            else:
                thread = threading.Thread(target=self.stabilize_video_standard,
                                          args=[to_stabilize, stabilized, session_id])
                thread.start()
        else:
            self.handle_get_not_found()

    def set_true_in_dict(self, session_id):
        self.ready_to_serve[session_id] = True
