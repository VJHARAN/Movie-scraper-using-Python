import threading
import re
import customtkinter as ctk
from playwright.sync_api import sync_playwright

class TorrentScraperV1(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Torrent Automator - Core Engine")
        self.geometry("520x400")
        
        ctk.CTkLabel(self, text="🍿 Homepage Torrent Scraper", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        self.entry = ctk.CTkEntry(self, placeholder_text="Enter movie name...", width=420, height=35)
        self.entry.pack(pady=10)
        
        self.btn = ctk.CTkButton(self, text="Search Homepage", command=self.launch_thread, height=40)
        self.btn.pack(pady=10)
        
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
                html_content = page.content()
                lines = re.split(r'<br\s*/?>', html_content, flags=re.IGNORECASE)
                
                for line in lines:
                    clean_line = re.sub(r'<[^>]+>', ' ', line).lower()
                    if all(word in clean_line for word in search_words):
                        match = re.search(r'href=["\'](https?://[^"\']+/forums/topic/[^"\']+)["\']', line, flags=re.IGNORECASE)
                        if match:
                            self.log(f"[FOUND HOMEPAGE ROW] URL: {match.group(1)}")
                            break
            except Exception as e:
                self.log(f"Error: {e}")
            browser.close()
        self.btn.configure(state="normal")

if __name__ == "__main__":
    TorrentScraperV1().mainloop()
