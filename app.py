import sys
import os
import re
import time
import threading
import requests
import urllib.parse
import customtkinter as ctk
from playwright.sync_api import sync_playwright
from qbittorrentapi import Client

VIDEO_PRIORITIES = ["true web-dl", "nf web-dl", "web-dl", "uhd", "bluray", "hd", "webrip", "hdrip", "rips"]
AUDIO_PRIORITIES = ["atmos", "ddp5.1", "dd+5.1", "dd5.1", "aac"]

THEATER_PRINT_KEYWORDS = [
    "cam", "predvd", "hq predvd", "dvdscr", "tc", "hdcam", 
    "hq pre-hd", "clean audio", "(hq clean)", "hq clean",
    "trailer", "official trailer", "teaser", "official teaser", "promo"
]

QBIT_HOST = "http://localhost:8080"
QBIT_USER = "admin"
QBIT_PASS = "adminadmin"

class UniversalPreciseScraper(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Universal TamilMV Automator (Size-Restricted Edition)")
        self.geometry("540x420")
        self.resizable(False, False)
        
        ctk.CTkLabel(self, text="🍿 Streamline Movie Downloader", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        self.entry = ctk.CTkEntry(self, placeholder_text="Enter movie name (e.g., minnal murali malayalam)...", width=420, height=35)
        self.entry.pack(pady=10)
        
        self.btn = ctk.CTkButton(self, text="Fetch & Send to qBittorrent", command=self.launch_thread, height=40, width=420, font=ctk.CTkFont(weight="bold"), anchor="center")
        self.btn.pack(pady=10, padx=20)
        
        self.output = ctk.CTkTextbox(self, width=480, height=220, font=ctk.CTkFont(family="Courier", size=11))
        self.output.pack(pady=10)
        self.log("System Ready. Enter your movie string above.")

    def log(self, text):
        self.output.insert("end", f"{text}\n")
        self.output.see("end")

    def launch_thread(self):
        title = self.entry.get().strip()
        if not title:
            return
        self.btn.configure(state="disabled")
        threading.Thread(target=self.core_worker, args=(title,), daemon=True).start()

    def core_worker(self, search_title):
        domains = ["https://www.1tamilmv.cards", "https://www.1tamilmv.taxi", "https://www.1tamilmv.pm"]
        search_words = [w.strip().lower() for w in search_title.lower().split() if len(w.strip()) > 1]
        
        with sync_playwright() as p:
            chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            browser = p.chromium.launch(headless=True, executable_path=chrome_path)
            page = browser.new_page()
            
            base_url = None
            for dom in domains:
                try:
                    res = page.goto(dom, wait_until="commit", timeout=6000)
                    if res and res.status < 400:
                        base_url = dom
                        break
                except Exception:
                    continue
            
            if not base_url:
                self.log("[FATAL] All domain mirrors are unreachable.")
                browser.close()
                self.btn.configure(state="normal")
                return

            self.log(f"Connected to mirror: {base_url}")
            page.wait_for_load_state("networkidle")
            
            self.log("Phase 2A: Scanning homepage index rows...")
            html_content = page.content()
            lines = re.split(r'<br\s*/?>', html_content, flags=re.IGNORECASE)
            
            homepage_href = None
            for line in lines:
                clean_line_text = re.sub(r'<[^>]+>', ' ', line).lower()
                if all(word in clean_line_text for word in search_words):
                    if any(banned in clean_line_text for banned in THEATER_PRINT_KEYWORDS):
                        continue
                    match = re.search(r'href=["\'](https?://[^"\']+/forums/topic/[^"\']+)["\']', line, flags=re.IGNORECASE)
                    if match:
                        homepage_href = match.group(1)
                        self.log("[FOUND] Located movie directly on the homepage feed.")
                        break

            if homepage_href:
                valid_links = self.extract_links_from_thread(page, homepage_href)
                browser.close()
                if valid_links:
                    self.log("Phase 4: Running qBittorrent Optimization...")
                    self.optimize_and_download(valid_links)
                else:
                    self.log("[FINISHED] No links match size/quality constraints inside thread.")
                self.btn.configure(state="normal")
                return

            encoded_query = urllib.parse.quote_plus(search_title)
            search_endpoint = f"{base_url}/search/?q={encoded_query}"
            self.log(f"Not on homepage fold. Phase 2B: Querying database engine via: {search_endpoint}")
            
            try:
                page.goto(search_endpoint, wait_until="networkidle", timeout=10000)
                search_cards = page.locator("a.sRow").all()
                
                candidate_urls = []
                for card in search_cards:
                    title_span = card.locator(".sTitle")
                    if not title_span.count():
                        continue
                        
                    text_content = (title_span.text_content() or "").lower()
                    normalized_text = " ".join(text_content.split())
                    
                    if all(word in normalized_text for word in search_words):
                        if any(banned in normalized_text for banned in THEATER_PRINT_KEYWORDS):
                            continue
                            
                        href = card.get_attribute("href") or ""
                        if href:
                            candidate_urls.append((href, normalized_text))

                for href, name in candidate_urls:
                    self.log(f"Testing candidate thread: {name[:45]}...")
                    valid_links = self.extract_links_from_thread(page, href)
                    
                    if valid_links:
                        self.log(f"[SUCCESS] Found valid release configurations inside: {name[:40]}...")
                        browser.close()
                        self.log("Phase 4: Running qBittorrent Optimization...")
                        self.optimize_and_download(valid_links)
                        self.btn.configure(state="normal")
                        return
            except Exception as e:
                self.log(f"[SEARCH ERROR] Query extraction execution failed: {str(e)}")

            browser.close()
            self.log(f"[FINISHED] Spent all card candidates. No matching releases found.")
            self.btn.configure(state="normal")

    def extract_links_from_thread(self, page, url):
        try:
            page.goto(url, wait_until="networkidle", timeout=10000)
            thread_title_element = page.locator("h1.ipsType_pageTitle, title")
            full_context_text = ""
            if thread_title_element.count():
                full_context_text = (thread_title_element.first.text_content() or "").lower()
                
            all_links = page.locator("a").all()
            valid_links = []
            
            for link in all_links:
                href = link.get_attribute("href") or ""
                label = (link.text_content() or "").lower()
                
                if href.startswith("magnet:") or "attachment.php?id=" in href:
                    if any(banned in label for banned in THEATER_PRINT_KEYWORDS):
                        continue
                    if "1080p" in label:
                        if "malayalam" in full_context_text or "tamil" in full_context_text or "malayalam" in label or "tamil" in label:
                            size_match = re.search(r'(\d+(?:\.\d+)?)\s*gb', label)
                            if size_match:
                                size_gb = float(size_match.group(1))
                                if size_gb > 5.0:
                                    continue
                                    
                        valid_links.append({"label": label, "url": href})
            return valid_links
        except Exception:
            return []

    def optimize_and_download(self, links):
        candidates = []
        found_profile_log = ""
        
        for source in VIDEO_PRIORITIES:
            for codec in AUDIO_PRIORITIES:
                candidates = [item for item in links if "untouched" in item["label"] and source in item["label"] and codec in item["label"]]
                if candidates:
                    found_profile_log = f"UNTOUCHED + {source.upper()} + {codec.upper()}"
                    break
            if candidates:
                break
                
        if not candidates:
            for source in VIDEO_PRIORITIES:
                for codec in AUDIO_PRIORITIES:
                    candidates = [item for item in links if source in item["label"] and codec in item["label"]]
                    if candidates:
                        found_profile_log = f"{source.upper()} + {codec.upper()}"
                        break
                if candidates:
                    break

        if not candidates:
            self.log("[FINISHED] No links match your parameters.")
            return

        try:
            qb = Client(host=QBIT_HOST, username=QBIT_USER, password=QBIT_PASS)
            qb.auth_log_in()
            hashes_to_track = []
            
            for item in candidates:
                url = item["url"]
                if url.startswith("magnet:"):
                    qb.torrents_add(urls=url, is_paused=True)
                    info_hash = re.search(r'btih:([a-fA-F0-9]+)', url)
                    if info_hash:
                        hashes_to_track.append(info_hash.group(1).lower())
                        
            time.sleep(6)
            all_torrents = qb.torrents_info()
            candidate_torrents = [t for t in all_torrents if t.hash.lower() in hashes_to_track]

            if not candidate_torrents:
                return

            candidate_torrents.sort(key=lambda x: x.num_seeds, reverse=True)
            best_torrent = candidate_torrents[0]
            
            self.log(f"\n🏆 WINNER: {best_torrent.name[:50]}... with {best_torrent.num_seeds} seeds!")
            qb.torrents_resume(torrent_hashes=best_torrent.hash)
            
            if len(candidate_torrents) > 1:
                losers = [t.hash for t in candidate_torrents[1:]]
                qb.torrents_delete(delete_files=True, torrent_hashes=losers)
                
            self.log("[SUCCESS] Handoff pipeline complete!")
        except Exception as err:
            self.log(f"[INJECTION ERROR] Analytics failed: {err}")

if __name__ == "__main__":
    UniversalPreciseScraper().mainloop()
