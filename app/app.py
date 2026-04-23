from shiny import App, render, ui, reactive
from pathlib import Path
import os
import sys
import requests

# Allow imports from src/
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_TIMEOUT = 120
sys.path.append(str(SRC_DIR))


def api_search(query: str, method: str, top_k: int = 3):
    response = requests.post(
        f"{API_BASE_URL}/search",
        json={"query": query, "method": method, "top_k": top_k},
        timeout=API_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("results", [])


def api_rag(question: str, method: str, top_k: int = 5):
    response = requests.post(
        f"{API_BASE_URL}/rag",
        json={"question": question, "method": method, "top_k": top_k},
        timeout=API_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()

SHARED_CSS = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 2rem 0;
    }

    .container-fluid {
        max-width: 900px;
        margin: 0 auto;
    }

    /* --- Tabs --- */
    .nav-tabs {
        border: none;
        background: rgba(255,255,255,0.15);
        border-radius: 16px;
        padding: 0.4rem;
        display: flex;
        gap: 0.25rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }

    .nav-tabs .nav-item .nav-link {
        border: none;
        border-radius: 12px;
        color: rgba(255,255,255,0.75);
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.6rem 1.4rem;
        transition: all 0.25s ease;
        background: transparent;
    }

    .nav-tabs .nav-item .nav-link:hover {
        color: white;
        background: rgba(255,255,255,0.15);
    }

    .nav-tabs .nav-item .nav-link.active {
        background: white;
        color: #764ba2;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* --- Cards --- */
    .search-container, .results-container, .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
    }

    h2 {
        color: #1a202c;
        font-weight: 700;
        font-size: 2rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .subtitle {
        color: #718096;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    .form-control {
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .form-control:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
    }

    .form-group label {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    .shiny-input-radiogroup {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .radio { margin: 0 !important; }

    .radio label {
        background: #f7fafc;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        display: inline-block;
    }

    .radio input:checked + span {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }

    .radio label:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }

    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        padding: 0.75rem 2.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }

    .btn-primary:active { transform: translateY(0); }

    .status-box {
        background: #f7fafc;
        border-left: 4px solid #667eea;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        color: #2d3748;
        font-weight: 500;
    }

    .results-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }

    table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-top: 1rem;
    }

    thead th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        font-weight: 600;
        text-align: left;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    thead th:first-child { border-radius: 12px 0 0 0; }
    thead th:last-child  { border-radius: 0 12px 0 0; }

    tbody td {
        padding: 1rem;
        border-bottom: 1px solid #e2e8f0;
        color: #2d3748;
    }

    tbody tr { transition: all 0.2s ease; }

    tbody tr:hover {
        background: #f7fafc;
        transform: scale(1.01);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    tbody tr:last-child td { border-bottom: none; }
    tbody tr:last-child td:first-child { border-radius: 0 0 0 12px; }
    tbody tr:last-child td:last-child  { border-radius: 0 0 12px 0; }

    .score-badge, .rating-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }

    .rating-badge {
        background: #fbbf24;
        color: white;
        padding: 0.25rem 0.6rem;
    }

    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, transparent, #e2e8f0, transparent);
        margin: 2rem 0;
    }

    /* ===== CHAT STYLES ===== */

    .chat-window {
        height: 480px;
        overflow-y: auto;
        padding: 1rem;
        background: #f7fafc;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        margin-bottom: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        scroll-behavior: smooth;
    }

    .chat-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #a0aec0;
        font-size: 0.95rem;
        gap: 0.5rem;
        text-align: center;
    }

    .chat-empty .chat-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    /* Bubbles */
    .bubble-row {
        display: flex;
        align-items: flex-end;
        gap: 0.6rem;
    }

    .bubble-row.user   { flex-direction: row-reverse; }
    .bubble-row.assistant { flex-direction: row; }

    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }

    .avatar.user-avatar {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }

    .avatar.bot-avatar {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
    }

    .bubble {
        max-width: 72%;
        padding: 0.85rem 1.1rem;
        border-radius: 18px;
        font-size: 0.93rem;
        line-height: 1.55;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        white-space: pre-wrap;
        word-break: break-word;
    }

    .bubble.user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
    }

    .bubble.bot-bubble {
        background: white;
        color: #2d3748;
        border: 1.5px solid #e2e8f0;
        border-bottom-left-radius: 4px;
    }

    .bubble.typing-bubble {
        background: white;
        border: 1.5px solid #e2e8f0;
        color: #a0aec0;
        font-style: italic;
        border-bottom-left-radius: 4px;
    }

    /* Input row */
    .chat-input-row {
        display: flex;
        gap: 0.75rem;
        align-items: flex-end;
    }

    .chat-input-row .form-control {
        flex: 1;
        resize: none;
        min-height: 48px;
        max-height: 120px;
        padding: 0.75rem 1rem;
    }

    .chat-input-row .btn-primary {
        padding: 0.75rem 1.5rem;
        flex-shrink: 0;
    }

    /* RAG method pills */
    .rag-method-row {
        display: flex;
        gap: 0.6rem;
        margin-bottom: 1.25rem;
        flex-wrap: wrap;
    }

    .rag-method-pill {
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 2px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.2s ease;
        background: #f7fafc;
        color: #4a5568;
    }

    .rag-method-pill:hover {
        border-color: #667eea;
        color: #667eea;
    }

    /* Clear button */
    .btn-ghost {
        background: transparent;
        border: 2px solid #e2e8f0;
        color: #718096;
        padding: 0.5rem 1.2rem;
        border-radius: 10px;
        font-weight: 500;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .btn-ghost:hover {
        border-color: #ef4444;
        color: #ef4444;
        background: #fff5f5;
    }
"""

# ── UI ────────────────────────────────────────────────────────────────────────

app_ui = ui.page_fluid(
    ui.tags.head(ui.tags.style(SHARED_CSS)),

    ui.navset_tab(

        # ── Tab 1: Search ──────────────────────────────────────────────────
        ui.nav_panel(
            "🔍 Search",
            ui.div(
                {"class": "search-container"},
                ui.h2("🔍 Product Search"),
                ui.p("Search through beauty product reviews using advanced AI", {"class": "subtitle"}),

                ui.input_text(
                    "query",
                    "What are you looking for?",
                    placeholder="e.g., blue sunglasses, moisturizer for dry skin..."
                ),
                ui.input_radio_buttons(
                    "method",
                    "Search Method:",
                    {"bm25": "⚡ BM25", "semantic": "🧠 Semantic", "hybrid": "🔮 Hybrid"},
                    selected="bm25",
                    inline=True
                ),
                ui.input_action_button("search", "Search", class_="btn-primary"),
                ui.div({"class": "status-box"}, ui.output_text("status")),
            ),
            ui.div({"class": "results-container"}, ui.output_ui("results")),
        ),

        # ── Tab 2: RAG Chat ────────────────────────────────────────────────
        ui.nav_panel(
            "🤖 RAG Chat",
            ui.div(
                {"class": "chat-container"},
                ui.h2("🤖 RAG Chat"),
                ui.p(
                    "Ask questions about beauty products — answers are grounded in real reviews.",
                    {"class": "subtitle"}
                ),

                # Method selector
                ui.input_radio_buttons(
                    "rag_method",
                    "Retrieval Method:",
                    {
                        "semantic": "🧠 Semantic RAG",
                        "hybrid":   "🔮 Hybrid RAG (BM25 + Semantic)"
                    },
                    selected="semantic",
                    inline=True
                ),

                # Chat window
                ui.div({"class": "chat-window", "id": "chat-window"}, ui.output_ui("chat_messages")),

                # Input row
                ui.div(
                    {"class": "chat-input-row"},
                    ui.input_text(
                        "chat_input",
                        label=None,
                        placeholder="Ask about a product, ingredient, or recommendation…"
                    ),
                    ui.input_action_button("chat_send", "Send ➤", class_="btn-primary"),
                ),

                ui.tags.br(),
                ui.input_action_button("chat_clear", "🗑 Clear conversation", class_="btn-ghost"),
            ),
        ),
    )
)


# ── Server ────────────────────────────────────────────────────────────────────

def server(input, output, session):

    # ── Search tab ──────────────────────────────────────────────────────────

    @reactive.calc
    @reactive.event(input.search)
    def run_search():
        query = input.query().strip()
        if not query:
            return None
        method = input.method()
        return api_search(query, method, top_k=3)

    @output
    @render.text
    def status():
        if input.search() == 0:
            return "👋 Ready to search! Enter your query above and select a search method."
        if not input.query().strip():
            return "⚠️ Please enter a search query."
        return f"✨ Showing top 3 results for '{input.query()}' using {input.method().upper()} search"

    @output
    @render.ui
    def results():
        res = run_search()
        if res is None:
            return ui.div()
        if not res:
            return ui.div(
                {"class": "status-box"},
                "No results found for your query."
            )

        score_col = next(
            (c for c in ("hybrid_score", "score", "distance") if any(c in row for row in res)),
            None
        )
        score_header = {"distance": "Distance", "hybrid_score": "Hybrid Score"}.get(score_col, "Score")

        rows = []
        for row in res:
            score_display = ""
            score_color = "#10b981"
            if score_col:
                score_val = row.get(score_col)
                if score_val is None and score_col == "hybrid_score":
                    score_val = row.get("score")
                elif score_val is None and score_col == "distance":
                    score_val = row.get("score")
                elif score_val is None and score_col == "score":
                    score_val = row.get("score")

                if score_val is not None:
                    score_display = f"{float(score_val):.3f}"
                    if score_col == "distance":
                        score_color = "#ef4444" if float(score_val) > 1 else "#10b981"
                    else:
                        score_color = "#10b981" if float(score_val) > 0.5 else "#f59e0b"

            rating_val = row.get("rating")
            rating_display = f"⭐ {float(rating_val):.1f}" if rating_val is not None else "N/A"
            title = str(row.get("product_title", ""))
            text = str(row.get("text", ""))
            rows.append(
                ui.tags.tr(
                    ui.tags.td(ui.tags.strong(title[:60] + "..." if len(title) > 60 else title)),
                    ui.tags.td(text[:100] + "..." if len(text) > 100 else text),
                    ui.tags.td(
                        ui.tags.span(
                            score_display,
                            {"class": "score-badge", "style": f"background:{score_color};color:white;"}
                        ) if score_display else ""
                    ),
                    ui.tags.td(ui.tags.span(rating_display, {"class": "rating-badge"})),
                )
            )

        return ui.tags.table(
            ui.tags.thead(ui.tags.tr(
                ui.tags.th("Product Title"),
                ui.tags.th("Review"),
                ui.tags.th(score_header),
                ui.tags.th("Rating"),
            )),
            ui.tags.tbody(*rows),
        )

    # ── RAG Chat tab ────────────────────────────────────────────────────────

    # Reactive list of {"role": "user"|"assistant", "content": str}
    chat_history = reactive.value([])

    @reactive.effect
    @reactive.event(input.chat_clear)
    def _clear():
        chat_history.set([])

    @reactive.effect
    @reactive.event(input.chat_send)
    def _send():
        question = input.chat_input().strip()
        if not question:
            return

        # Append user message immediately
        history = chat_history.get().copy()
        history.append({"role": "user", "content": question})
        # Add a temporary typing indicator
        history.append({"role": "assistant", "content": "__typing__"})
        chat_history.set(history)

        # Call the FastAPI backend
        method = input.rag_method()
        try:
            response = api_rag(question, method, top_k=5)
            answer = response.get("answer", "")
        except Exception as e:
            answer = f"⚠️ Something went wrong: {e}"

        # Replace typing indicator with real answer
        history = chat_history.get().copy()
        # Remove last __typing__ entry and replace with real answer
        if history and history[-1]["content"] == "__typing__":
            history[-1]["content"] = answer
        else:
            history.append({"role": "assistant", "content": answer})
        chat_history.set(history)

        # Clear the input box
        ui.update_text("chat_input", value="")

    @output
    @render.ui
    def chat_messages():
        history = chat_history.get()

        if not history:
            return ui.div(
                {"class": "chat-empty"},
                ui.div("🛍️", {"class": "chat-icon"}),
                ui.p("Ask me anything about beauty products!"),
                ui.p(
                    "e.g. \"What's a good moisturizer for sensitive skin?\"",
                    style="font-size:0.85rem; color:#cbd5e0;"
                ),
            )

        bubbles = []
        for msg in history:
            role    = msg["role"]
            content = msg["content"]
            is_user = role == "user"

            avatar = ui.div(
                "👤" if is_user else "🤖",
                {"class": f"avatar {'user-avatar' if is_user else 'bot-avatar'}"}
            )

            if content == "__typing__":
                bubble = ui.div("✦ Thinking…", {"class": "bubble typing-bubble"})
            else:
                bubble = ui.div(
                    content,
                    {"class": f"bubble {'user-bubble' if is_user else 'bot-bubble'}"}
                )

            bubbles.append(
                ui.div(
                    avatar,
                    bubble,
                    {"class": f"bubble-row {'user' if is_user else 'assistant'}"}
                )
            )

        # Auto-scroll to bottom via inline JS
        scroll_js = ui.tags.script(
            """
            (function() {
                var w = document.getElementById('chat-window');
                if (w) w.scrollTop = w.scrollHeight;
            })();
            """
        )
        return ui.div(*bubbles, scroll_js)


app = App(app_ui, server)