import threading
import re
import customtkinter as ctk
from playwright.sync_api import sync_playwright

THEATER_PRINT_KEYWORDS = ["cam", "predvd", "hq predvd", "dvdscr", "tc", "hdcam", "trailer", "teaser", "promo", "official trailer"]

class TorrentScraperV1(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Torrent Automator - Core Engine")
        self.geometry("520x400")
        
        ctk.CTkLabel(self, text="🍿 Homepage Torrent Scraper", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        self.entry = ctk.CTkEntry(self, placeholder_text="Enter movie name...", width=420, height=35)
        self.entry.pack(pady=10)
        
        self.btn = ctk.CTkButton(self, text="Fetch & Send to qBittorrent", command=self.launch_thread, height=40, width=420, anchor="center")
        self.btn.pack(pady=10, padx=20)
        
        self.output = ctk.CTkTextbox(self, width=480, height=220)
        self.output.pack(pady=10)

    def log(self, text):
        self.output.insert("end", f"{text}\n")
        self.output.see("end")

    def launch_thread(self):
        title = self.entry.get().strip()
        if title:
            self.btn.configure(state="disabled")
            threading.Thread(target=self.worker, args=(title,), daemon=True).start()

    def worker(self, search_title):
        url = "https://www.1tamilmv.cards"
        search_words = [w.strip().lower() for w in search_title.lower().split() if len(w.strip()) > 1]
      
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
            page = browser.new_page()
            try:
                page.goto(url, timeout=8000)
                # Target micro line-containers to completely prevent cross-movie matching slips
                containers = page.locator("strong, p, li, tr").all()
                for box in containers:
                    text = (box.text_content() or "").lower()
                    if all(word in text for word in search_words):
                        if any(banned in text for banned in THEATER_PRINT_KEYWORDS):
                            continue
                        anchors = box.locator("a").all()
                        for a in anchors:
                            href = a.get_attribute("href") or ""
                            if "/forums/topic/" in href:
                                topic_href = href
                                break
                # Phase 2B Fallback Search Engine Routing
                if not topic_href:
                    encoded_query = urllib.parse.quote_plus(search_title)
                    search_endpoint = f"{base_url}/search/?q={encoded_query}"
                    page.goto(search_endpoint, wait_until="networkidle")
                    
                    search_cards = page.locator("a.sRow").all()
                    for card in search_cards:
                        title_span = card.locator(".sTitle")
                        if title_span.count():
                            text_content = (title_span.text_content() or "").lower()
                            if all(word in text_content for word in search_words):
                                topic_href = card.get_attribute("href")
                                break
                                
            except Exception as e:
                self.log(f"Error: {e}")
            browser.close()
        self.btn.configure(state="normal")

if __name__ == "__main__":
    TorrentScraperV1().mainloop()
