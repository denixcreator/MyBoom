import http.server
import socketserver
import urllib.parse
import os

PORT = 8080
FIREWORKS_FILE = "fireworks.txt"
OWNER_USERNAME = "admin"
OWNER_PASSWORD = "fireboom"

# HTML templates
def get_home_page():
    return """
    <html>
    <head>
        <title>MyBoom</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: white; text-align: center; padding: 40px; }
            h1 { font-size: 3rem; color: #ff4500; font-family: 'Impact', sans-serif; }
            a.button {
                display: inline-block; padding: 15px 30px; background: #ff4500; color: white; text-decoration: none;
                border-radius: 10px; font-size: 1.2rem; margin: 10px;
            }
            a.button:hover { background: #cc3700; }
        </style>
    </head>
    <body>
        <h1>🔥 Welcome to MyBoom!</h1>
        <p>Explore epic fireworks or log in to add your own!</p>
        <a href="/gallery" class="button">View Gallery</a>
        <a href="/login" class="button">Owner Login</a>
    </body>
    </html>
    """

def get_login_page():
    return """
    <html>
    <head>
        <title>Login - MyBoom</title>
        <style>
            body { background: #111; color: white; font-family: Arial; text-align: center; padding: 40px; }
            input, button { padding: 10px; font-size: 1rem; margin: 10px; border-radius: 6px; border: none; }
            button { background: #ff4500; color: white; cursor: pointer; }
            button:hover { background: #cc3700; }
        </style>
    </head>
    <body>
        <h2>Owner Login</h2>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Log In</button>
        </form>
    </body>
    </html>
    """

def get_add_page():
    return """
    <html>
    <head>
        <title>Add Firework</title>
        <style>
            body { background: #111; color: white; font-family: Arial; text-align: center; padding: 40px; }
            input, textarea, select { padding: 10px; font-size: 1rem; margin: 10px; width: 80%; max-width: 400px; border-radius: 6px; border: none; }
            button { padding: 10px 20px; background: #ff4500; color: white; border: none; border-radius: 6px; cursor: pointer; }
            button:hover { background: #cc3700; }
        </style>
    </head>
    <body>
        <h2>Add a New Firework</h2>
        <form method="POST" action="/add">
            <input type="text" name="name" placeholder="Firework Name" required><br>
            <textarea name="description" placeholder="Description" rows="4" required></textarea><br>
            <input type="text" name="image" placeholder="Image URL" required><br>
            <select name="category">
                <option value="Rockets">Rockets</option>
                <option value="Sparklers">Sparklers</option>
                <option value="Fountains">Fountains</option>
                <option value="Other">Other</option>
            </select><br>
            <button type="submit">Add Firework</button>
        </form>
        <br>
        <a href="/gallery" style="color:#ff4500;">Back to Gallery</a>
    </body>
    </html>
    """

def get_gallery_page(items_html, search="", selected_category="All"):
    return f"""
    <html>
    <head>
        <title>Gallery - MyBoom</title>
        <style>
            body {{ background: #000; color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; }}
            .search-bar {{
                text-align: center; margin-bottom: 20px;
            }}
            .search-bar input, .search-bar select {{
                padding: 10px; border-radius: 8px; font-size: 1rem; border: none;
            }}
            .search-bar button {{
                padding: 10px 20px; background: #ff4500; color: white; border: none; border-radius: 8px;
                cursor: pointer;
            }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .card {{ background: #222; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 0 8px #ff4500; }}
            img {{ max-width: 100%; border-radius: 10px; }}
            h2 {{ color: #ff4500; margin: 10px 0 5px; }}
            a {{ color: #ff4500; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h1>🎇 Fireworks Gallery 🎇</h1>
        <div class="search-bar">
            <form method="GET" action="/gallery">
                <input type="text" name="search" placeholder="Search..." value="{search}">
                <select name="category">
                    <option {"selected" if selected_category == "All" else ""}>All</option>
                    <option {"selected" if selected_category == "Rockets" else ""}>Rockets</option>
                    <option {"selected" if selected_category == "Sparklers" else ""}>Sparklers</option>
                    <option {"selected" if selected_category == "Fountains" else ""}>Fountains</option>
                    <option {"selected" if selected_category == "Other" else ""}>Other</option>
                </select>
                <button type="submit">Search</button>
            </form>
        </div>
        <div class="grid">
            {items_html}
        </div>
        <br><a href="/">Back to Home</a>
    </body>
    </html>
    """

def render_gallery_items(search="", category="All", logged_in=False):
    if not os.path.exists(FIREWORKS_FILE):
        return "<p>No fireworks yet!</p>"

    items = ""
    with open(FIREWORKS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for index, line in enumerate(lines):
        parts = line.strip().split(" | ")
        if len(parts) == 4:
            name, desc, img, cat = parts
            if (search.lower() in name.lower() or search.lower() in desc.lower()) and (category == "All" or category == cat):
                delete_button = f"""
                <form method="POST" action="/delete" style="margin-top:10px;">
                    <input type="hidden" name="index" value="{index}">
                    <button type="submit" style="background:#880000;border:none;color:white;padding:6px 12px;border-radius:6px;">🗑 Delete</button>
                </form>
                """ if logged_in else ""
                items += f"""
                <div class="card">
                    <img src="{img}" alt="{name}">
                    <h2>{name}</h2>
                    <p><em>{cat}</em></p>
                    <p>{desc}</p>
                    {delete_button}
                </div>
                """
    return items if items else "<p>No matching fireworks found.</p>"

# HTTP Request Handler
class MyBoomHandler(http.server.SimpleHTTPRequestHandler):
    logged_in = False

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        search = query.get("search", [""])[0]
        category = query.get("category", ["All"])[0]

        if path == "/":
            self.respond(get_home_page())
        elif path == "/login":
            self.respond(get_login_page())
        elif path == "/add" and MyBoomHandler.logged_in:
            self.respond(get_add_page())
        elif path == "/gallery":
            items = render_gallery_items(search, category, MyBoomHandler.logged_in)
            self.respond(get_gallery_page(items, search, category))
        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        data = urllib.parse.parse_qs(body)

        if self.path == "/login":
            user = data.get("username", [""])[0]
            pw = data.get("password", [""])[0]
            if user == OWNER_USERNAME and pw == OWNER_PASSWORD:
                MyBoomHandler.logged_in = True
                self.redirect("/add")
            else:
                self.respond("<h2>Login Failed</h2><a href='/login'>Try again</a>")
        elif self.path == "/add" and MyBoomHandler.logged_in:
            name = data.get("name", [""])[0]
            desc = data.get("description", [""])[0]
            image = data.get("image", [""])[0]
            category = data.get("category", ["Other"])[0]
            with open(FIREWORKS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{name} | {desc} | {image} | {category}\n")
            self.redirect("/gallery")
        elif self.path == "/delete" and MyBoomHandler.logged_in:
            index = int(data.get("index", ["-1"])[0])
            if os.path.exists(FIREWORKS_FILE):
                with open(FIREWORKS_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                if 0 <= index < len(lines):
                    del lines[index]
                    with open(FIREWORKS_FILE, "w", encoding="utf-8") as f:
                        f.writelines(lines)
            self.redirect("/gallery")
        else:
            self.send_error(403, "Forbidden")

    def respond(self, content):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def redirect(self, path):
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()

# Run the server
with socketserver.TCPServer(("", PORT), MyBoomHandler) as httpd:
    print(f"🌐 Serving MyBoom at http://localhost:{PORT}")
    httpd.serve_forever()
