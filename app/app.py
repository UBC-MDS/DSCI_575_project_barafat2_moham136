from shiny import App, render, ui, reactive
from pathlib import Path
import sys

# Allow imports from src/
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))


from search import bm25_search
from semantic_search import semantic_search

app_ui = ui.page_fluid(
    ui.h2("Product Search"),
    ui.input_text("query", "Enter a query:", ""),
    ui.input_radio_buttons(
        "method",
        "Select a search method:",{
            "bm25":"BM25",
            "semantic":"Semantic",
            "hybrid":"Hybrid"
        },
        selected="bm25",
        inline=True
    ),
    ui.input_action_button("search", "Search"),
    ui.hr(),
    ui.output_text_verbatim("status"),
    ui.output_table("results")
)


def server(input, output, session):
    @reactive.calc
    @reactive.event(input.search)
    def run_search():
        query = input.query().strip()
        top_k = 3
        method = input.method()
        if not query:
            return "Please enter a query.", None
        if method == "bm25":
            # Call BM25 search function
            return(bm25_search(query, top_k))
        elif method == "semantic":
            # Call semantic search function
            return(semantic_search(query, top_k))
        elif method == "hybrid":
            return(bm25_search(query, top_k)) # Placeholder for hybrid search - Will be replaced with actual implementation

        return None
    
    @output
    @ui.render_text
    def status():
        if input.search() == 0:
            return "Ready to search."
        if not input.query().strip():
            return "Please enter a query."
        return f"Showing top 3 results for '{input.query()}' using {input.method()} search."
    
    @output
    @ui.render_table
    def results():
        res = run_search()
        if res is None:
            return None
        return res
        
    



app = App(app_ui, server)


