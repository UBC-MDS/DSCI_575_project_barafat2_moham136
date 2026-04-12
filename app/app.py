from shiny import App, render, ui, reactive
from pathlib import Path
import sys

# Allow imports from src/
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

from search import bm25_search
from semantic_search import semantic_search
from hybrid_search import search_hybrid

# The custom CSS for beautification was created by CLAUDE


app_ui = ui.page_fluid(
    # Custom CSS for modern styling
    ui.tags.head(
        ui.tags.style("""
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
            
            .search-container {
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
            
            .radio {
                margin: 0 !important;
            }
            
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
            
            .btn-primary:active {
                transform: translateY(0);
            }
            
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
            
            thead th:first-child {
                border-radius: 12px 0 0 0;
            }
            
            thead th:last-child {
                border-radius: 0 12px 0 0;
            }
            
            tbody td {
                padding: 1rem;
                border-bottom: 1px solid #e2e8f0;
                color: #2d3748;
            }
            
            tbody tr {
                transition: all 0.2s ease;
            }
            
            tbody tr:hover {
                background: #f7fafc;
                transform: scale(1.01);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            tbody tr:last-child td {
                border-bottom: none;
            }
            
            tbody tr:last-child td:first-child {
                border-radius: 0 0 0 12px;
            }
            
            tbody tr:last-child td:last-child {
                border-radius: 0 0 12px 0;
            }
            
            .score-badge {
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.85rem;
            }
            
            .rating-badge {
                display: inline-block;
                background: #fbbf24;
                color: white;
                padding: 0.25rem 0.6rem;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.85rem;
            }
            
            hr {
                border: none;
                height: 2px;
                background: linear-gradient(to right, transparent, #e2e8f0, transparent);
                margin: 2rem 0;
            }
        """)
    ),
    
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
            {
                "bm25": "⚡ BM25",
                "semantic": "🧠 Semantic",
                "hybrid": "🔮 Hybrid"
            },
            selected="bm25",
            inline=True
        ),
        
        ui.input_action_button("search", "Search", class_="btn-primary"),
        
        ui.div(
            {"class": "status-box"},
            ui.output_text("status")
        ),
    ),
    
    ui.div(
        {"class": "results-container"},
        ui.output_ui("results")
    )
)

def server(input, output, session):
    @reactive.calc
    @reactive.event(input.search)
    def run_search():
        query = input.query().strip()
        top_k = 3
        method = input.method()
        if not query:
            return None
        if method == "bm25":
            return bm25_search(query, top_k)
        elif method == "semantic":
            return semantic_search(query, top_k)
        elif method == "hybrid":
            return search_hybrid(query, top_k) 
        return None
    
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
        
        # Determine which score column to use
        score_col = None
        if 'score' in res.columns:
            score_col = 'score'
        elif 'distance' in res.columns:
            score_col = 'distance'
        elif 'hybrid_score' in res.columns:
            score_col = 'hybrid_score'
        
        # Build table rows
        rows = []
        for idx, row in res.iterrows():
            # Format score
            if score_col:
                score_val = row[score_col]
                if score_col == 'distance':
                    score_display = f"{score_val:.3f}"
                    score_color = "#ef4444" if score_val > 1 else "#10b981"
                else:
                    score_display = f"{score_val:.3f}"
                    score_color = "#10b981" if score_val > 0.5 else "#f59e0b"
            
            # Format rating
            rating_display = f"⭐ {row['rating']:.1f}" if 'rating' in res.columns else "N/A"
            
            rows.append(
                ui.tags.tr(
                    ui.tags.td(ui.tags.strong(row['product_title'][:60] + "..." if len(str(row['product_title'])) > 60 else row['product_title'])),
                    ui.tags.td(str(row['text'])[:100] + "..." if len(str(row['text'])) > 100 else row['text']),
                    ui.tags.td(
                        ui.tags.span(
                            score_display,
                            {"class": "score-badge", "style": f"background: {score_color}; color: white;"}
                        ) if score_col else ""
                    ),
                    ui.tags.td(
                        ui.tags.span(rating_display, {"class": "rating-badge"})
                    )
                )
            )
        
        # Score column header
        score_header = "Score"
        if score_col == 'distance':
            score_header = "Distance"
        elif score_col == 'hybrid_score':
            score_header = "Hybrid Score"
        
        return ui.tags.table(
            ui.tags.thead(
                ui.tags.tr(
                    ui.tags.th("Product Title"),
                    ui.tags.th("Review"),
                    ui.tags.th(score_header),
                    ui.tags.th("Rating")
                )
            ),
            ui.tags.tbody(*rows)
        )

app = App(app_ui, server)