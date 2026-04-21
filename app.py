from flask import Flask, request, render_template, render_template_string, redirect, url_for
import os

app = Flask(__name__)

# --- Simulated blog post database ---
POSTS = [
    {
        "id": 1,
        "title": "Welcome to ByteVault Blog",
        "author": "kaustav",
        "date": "April 10, 2026",
        "category": "Announcement",
        "content": """Welcome to ByteVault — your go-to place for developer stories, tutorials, and tech deep-dives.
We're a community-powered blog where anyone can share their knowledge. Stay curious, keep building.
This platform is still in beta — some features may be rough around the edges!""",
        "tags": ["welcome", "community", "tech"]
    },
    {
        "id": 2,
        "title": "Getting Started with Linux for Developers",
        "author": "secdaa",
        "date": "April 12, 2026",
        "category": "Linux",
        "content": """Linux is the backbone of modern software infrastructure. Whether you're deploying servers, writing scripts, or just daily-driving your development machine, understanding Linux fundamentals is essential.

In this post, we'll cover: filesystem structure, process management, permissions, and some quality-of-life tools every developer should know.

Start with learning your way around the terminal. The `ls`, `cd`, `pwd`, `cat`, `grep`, and `find` commands will be your best friends. Once you're comfortable, dive into shell scripting and cron jobs.""",
        "tags": ["linux", "beginner", "devops"]
    },
    {
        "id": 3,
        "title": "Why Python is Still Relevant in 2026",
        "author": "pr0grammer",
        "date": "April 15, 2026",
        "category": "Python",
        "content": """Despite the rise of Go, Rust, and TypeScript dominating certain niches, Python remains the Swiss Army knife of programming. Its ecosystem — from data science to web development to automation — is unmatched.

Flask and FastAPI make spinning up web services trivially easy. Libraries like Pandas, NumPy, and scikit-learn are the gold standard in data work. And with Python 3.12+, performance has improved significantly.

Don't write off Python. It's not going anywhere.""",
        "tags": ["python", "webdev", "opinion"]
    },
    {
        "id": 4,
        "title": "Exploring Docker: Containerize Everything",
        "author": "d0cker_d4ve",
        "date": "April 17, 2026",
        "category": "DevOps",
        "content": """Docker changed how we ship software. The idea is simple: package your application and its dependencies into a container that runs consistently anywhere.

In practice, this means no more "it works on my machine" excuses. Your dev, staging, and prod environments can be identical. Compose makes multi-service orchestration a breeze.

Start with the official docs, build a simple Dockerfile, and progressively work toward multi-stage builds and slim base images.""",
        "tags": ["docker", "containers", "devops"]
    },
]

FLAG_USER = os.environ.get("FLAG_USER", "ByteVault{SSTI_t0_RCE_1s_cl4ssic_n0cn34icyb74cy73yo8y7bcyw75bci3tbo4to?}")

# -------------------------------------------------------
# ROUTES
# -------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", posts=POSTS)

@app.route("/post/<int:post_id>")
def post(post_id):
    p = next((x for x in POSTS if x["id"] == post_id), None)
    if not p:
        return render_template("404.html"), 404
    return render_template("post.html", post=p)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    results = []
    if query:
        results = [p for p in POSTS if query.lower() in p["title"].lower() or query.lower() in p["content"].lower()]
    return render_template("search.html", posts=results, query=query)


@app.route("/author/<username>")
def author(username):
    author_posts = [p for p in POSTS if p["author"] == username]
    return render_template("author.html", username=username, posts=author_posts)

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/console", methods=["GET", "POST"])
def console():
    output = None
    code = ""
    error = None

    if request.method == "POST":
        code = request.form.get("code", "")

        # ⚠️  VULNERABLE: user-supplied `code` is injected directly into a
        #     Jinja2 template string via an f-string, then rendered.
        #     This means Jinja2 expressions inside `code` are evaluated —
        #     it is NOT actually executing Python. Classic SSTI.
        template = f"""
{{% extends "base.html" %}}
{{% block content %}}
<div class="console-wrapper">
  <div class="console-header">
    <span class="console-label">// ByteVault Python Sandbox</span>
    <span class="console-badge">BETA</span>
  </div>
  <div class="console-editor-section">
    <form method="POST" action="/console">
      <div class="editor-toolbar">
        <span class="editor-lang">Python 3.11</span>
        <button type="submit" class="btn-run">&#9654; Run</button>
      </div>
      <textarea name="code" class="code-editor" spellcheck="false" placeholder="# Write your Python code here&#10;print('Hello, ByteVault!')">{code}</textarea>
    </form>
  </div>
  <div class="console-output-section">
    <div class="output-toolbar">
      <span class="output-label">Output</span>
    </div>
    <div class="output-body">
      <pre class="output-pre">{code}</pre>
    </div>
  </div>
  <div class="console-notice">
    <span>&#9888;</span> This sandbox runs in a restricted environment. Imports, file I/O, and network calls are disabled for safety.
  </div>
</div>
{{% endblock %}}
"""
        try:
            return render_template_string(template)
        except Exception as e:
            error = str(e)

    return render_template("console.html", output=output, code=code, error=error)


# 404
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
