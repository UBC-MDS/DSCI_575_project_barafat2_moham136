from shiny import App, render, ui, reactive
from pathlib import Path
from bm25 import bm25_search          
from semantic import semantic_search 


# ---------------- DATA ----------------

BASE_DIR = Path(__file__).parent
 = BASE_DIR.parent / "data" / "raw" / 
csv_path.parent.mkdir(parents=True, exist_ok=True)
parquet_path = BASE_DIR.parent / "data" / "processed" / "ncr_ride_bookings.parquet"
clean_parquet_path = BASE_DIR.parent / "data" / "processed" / "ncr_ride_bookings_clean.parquet"



# ---------------- SERVER ----------------



# ---------------- APP ----------------
app = App(app_ui, server)