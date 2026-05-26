# Movie-scraper-using-Python🍿🚀

An automated web-scraping tool built with Python, CustomTkinter, and Playwright that dynamically maps high-quality digital releases from public forums and feeds them directly into your running qBittorrent client. 

The application bypasses unstable layout blocks, masks trailer/promotional noise, prioritizes user quality/audio profiles, checks tracker swarms for healthy seed configurations, and enforces storage safeguards dynamically.

## 🌟 Key Features

* **Dual-Engine Scraping:** Scans active homepage rows line-by-line using proximity block tracking. If a title has expired off the fold, it seamlessly switches engine configurations to crawl site archive index cards.
* **Smart Filter Matrix:** Automatically drops low-quality bootlegs (`cam`, `predvd`, `dvdscr`) and marketing fluff (`trailer`, `teaser`, `promo`).
* **Swarm Seed Optimization:** Instead of checking blindly, the app loads premium matching variants into qBittorrent in a *paused* state, waits 6 seconds to capture tracker updates, resumes the single highest-seeded torrent for optimal performance, and purges the stale links.
* **Storage Guards:** Enforces a strict conditional `5.0 GB` maximum ceiling rule specifically for Tamil and Malayalam profiles to protect local disk space.
* **Failover Domains:** Rotates through live alternative gateway mirrors automatically if a specific domain extension fails to handshake.
* **Async UI Architecture:** The `CustomTkinter` frontend runs decoupled from the scraping engine using concurrent Python `threading` routines to eliminate screen freezing.

## 🛠️ System Requirements & Infrastructure

* **Python 3.10+**
* **Google Chrome** installed at default path: `C:\Program Files\Google\Chrome\Application\chrome.exe`
* **qBittorrent Client** with WebUI enabled (`Tools` -> `Options` -> `WebUI` -> Allow access on `localhost:8080`)

## 🚀 Installation & Running

1. Install project dependencies:
   ```bash
   pip install customtkinter playwright qbittorrent-api requests
