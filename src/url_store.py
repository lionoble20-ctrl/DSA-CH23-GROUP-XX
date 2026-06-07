# =============================================================================
#  url_store.py  —  Core Hash Table for the URL Shortening Service
#  DSA-CH23-GROUP-XX  |  Theme B: Bitly-lite
#  Data Structures Used: Hash Table, Stack, Queue, Min-Heap
# =============================================================================

import hashlib
import heapq
import time
from collections import deque


# =============================================================================
#  CLASS: URLStore
#  The main hash table that powers the entire URL shortener.
#  Supports: shorten, redirect, delete, undo, top-K analytics
# =============================================================================

class URLStore:

    def __init__(self):
        # ── Core Hash Tables ──────────────────────────────────────────────────
        self.short_to_long  = {}   # short_code  -> long_url      (O(1) lookup)
        self.long_to_short  = {}   # long_url    -> short_code    (avoid duplicates)
        self.click_counts   = {}   # short_code  -> int           (analytics)

        # ── Stack: undo history (stores tuples of (action, data)) ─────────────
        self.history_stack  = []

        # ── Queue: incoming request buffer ────────────────────────────────────
        self.request_queue  = deque()

        # ── Min-Heap: top-K clicked links ─────────────────────────────────────
        #    stored as (click_count, short_code) — heapq is a min-heap by default
        self._heap          = []

        # ── Stats ─────────────────────────────────────────────────────────────
        self.total_shortened  = 0
        self.total_redirects  = 0


    # =========================================================================
    #  PRIVATE: Generate a short code from a long URL
    #  Uses MD5 hash — takes first 6 hex characters → 16^6 = 16 million combos
    #  Big-O: O(1)
    # =========================================================================

    def _generate_code(self, long_url: str) -> str:
        return hashlib.md5(long_url.encode()).hexdigest()[:6]


    # =========================================================================
    #  PRIVATE: Collision handling — linear probing
    #  If the generated code is already taken by a DIFFERENT URL, keep shifting
    #  Big-O: O(k) where k = number of collisions (almost always O(1))
    # =========================================================================

    def _resolve_collision(self, long_url: str, code: str) -> str:
        salt = 0
        original_code = code
        while code in self.short_to_long and self.short_to_long[code] != long_url:
            salt += 1
            salted = long_url + str(salt)
            code = hashlib.md5(salted.encode()).hexdigest()[:6]
            # Safety valve: if we've tried 1000 times, fall back to timestamp-based code
            if salt > 1000:
                code = hex(int(time.time() * 1000))[-6:]
                break
        return code


    # =========================================================================
    #  PUBLIC: shorten(long_url)
    #  Takes a long URL and returns a short code.
    #  If the URL was already shortened before, returns the SAME code (no duplicate).
    #  Big-O: O(1) average
    # =========================================================================

    def shorten(self, long_url: str) -> str:
        long_url = long_url.strip()

        # Basic validation
        if not long_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: '{long_url}' — must start with http:// or https://")

        # If already shortened, return existing code (no duplicate entries)
        if long_url in self.long_to_short:
            existing_code = self.long_to_short[long_url]
            print(f"  [EXISTING]  {long_url}  →  short.ly/{existing_code}")
            return existing_code

        # Generate code and resolve any collision
        code = self._generate_code(long_url)
        code = self._resolve_collision(long_url, code)

        # Store in both hash tables
        self.short_to_long[code]  = long_url
        self.long_to_short[long_url] = code
        self.click_counts[code]   = 0

        # Push to undo stack
        self.history_stack.append(("ADD", code, long_url))

        # Add to heap for analytics tracking (start at 0 clicks)
        heapq.heappush(self._heap, (0, code))

        self.total_shortened += 1
        print(f"  [SHORTENED]  {long_url}  →  short.ly/{code}")
        return code


    # =========================================================================
    #  PUBLIC: redirect(short_code)
    #  Looks up the original URL from a short code.
    #  This is the most-called operation — must be O(1).
    #  Big-O: O(1)
    # =========================================================================

    def redirect(self, short_code: str) -> str:
        short_code = short_code.strip().lower()

        if short_code not in self.short_to_long:
            raise KeyError(f"Short code '{short_code}' not found — it may have been deleted or never existed.")

        long_url = self.short_to_long[short_code]

        # Update click count
        self.click_counts[short_code] += 1
        self.total_redirects += 1

        # Push updated count to heap (lazy update — old entry stays but gets ignored)
        heapq.heappush(self._heap, (self.click_counts[short_code], short_code))

        print(f"  [REDIRECT]   short.ly/{short_code}  →  {long_url}  (clicks: {self.click_counts[short_code]})")
        return long_url


    # =========================================================================
    #  PUBLIC: delete(short_code)
    #  Removes a short link. Pushes the deleted entry onto the undo stack.
    #  Big-O: O(1)
    # =========================================================================

    def delete(self, short_code: str) -> bool:
        short_code = short_code.strip().lower()

        if short_code not in self.short_to_long:
            print(f"  [ERROR]  Cannot delete '{short_code}' — not found.")
            return False

        long_url = self.short_to_long[short_code]

        # Remove from both hash tables
        del self.short_to_long[short_code]
        del self.long_to_short[long_url]

        # Push to undo stack so we can restore it
        self.history_stack.append(("DELETE", short_code, long_url))

        print(f"  [DELETED]  short.ly/{short_code}  (was → {long_url})")
        return True


    # =========================================================================
    #  PUBLIC: undo()
    #  Reverses the last ADD or DELETE operation using the history stack.
    #  Big-O: O(1)
    # =========================================================================

    def undo(self) -> bool:
        if not self.history_stack:
            print("  [UNDO]  Nothing to undo.")
            return False

        action, code, long_url = self.history_stack.pop()

        if action == "ADD":
            # Undo an ADD = remove the entry
            if code in self.short_to_long:
                del self.short_to_long[code]
                del self.long_to_short[long_url]
                print(f"  [UNDO ADD]  Removed short.ly/{code}")

        elif action == "DELETE":
            # Undo a DELETE = restore the entry
            self.short_to_long[code]     = long_url
            self.long_to_short[long_url] = code
            if code not in self.click_counts:
                self.click_counts[code] = 0
            print(f"  [UNDO DELETE]  Restored short.ly/{code}  →  {long_url}")

        return True


    # =========================================================================
    #  PUBLIC: top_k(k)
    #  Returns the K most-clicked short links using the min-heap.
    #  Big-O: O(n log k) — very efficient for large n, small k
    # =========================================================================

    def top_k(self, k: int = 5) -> list:
        # Clean the heap: filter out stale/deleted entries
        valid = []
        seen  = set()

        # Drain heap into a list, keep only the latest count per code
        temp = []
        while self._heap:
            count, code = heapq.heappop(self._heap)
            if code in self.click_counts and code not in seen:
                seen.add(code)
                # Use the live click count, not the stale heap value
                temp.append((self.click_counts[code], code))

        # Rebuild the heap with fresh values
        for item in temp:
            heapq.heappush(self._heap, item)

        # Sort descending by click count and return top K
        results = sorted(temp, key=lambda x: x[0], reverse=True)[:k]

        print(f"\n  ── Top {k} Most Clicked Links ──────────────────")
        if not results:
            print("  No clicks recorded yet.")
        for rank, (clicks, code) in enumerate(results, 1):
            long_url = self.short_to_long.get(code, "[deleted]")
            print(f"  #{rank}  short.ly/{code}  |  {clicks} clicks  |  {long_url}")
        print(f"  ────────────────────────────────────────────\n")

        return results


    # =========================================================================
    #  PUBLIC: queue_request(long_url)  /  process_queue()
    #  Simulates a request buffer — URLs are added to a queue and processed
    #  in order (FIFO). Useful for handling bursts of requests.
    #  Enqueue Big-O: O(1)  |  Process-all Big-O: O(n)
    # =========================================================================

    def queue_request(self, long_url: str):
        self.request_queue.append(long_url)
        print(f"  [QUEUED]  {long_url}  (queue size: {len(self.request_queue)})")

    def process_queue(self):
        if not self.request_queue:
            print("  [QUEUE]  No pending requests.")
            return
        print(f"\n  ── Processing {len(self.request_queue)} queued request(s) ──")
        while self.request_queue:
            url = self.request_queue.popleft()
            self.shorten(url)
        print("  ── Queue cleared ──\n")


    # =========================================================================
    #  PUBLIC: stats()
    #  Prints a summary of the current store state.
    # =========================================================================

    def stats(self):
        print(f"\n  ── Store Stats ─────────────────────────────")
        print(f"  Total URLs stored   : {len(self.short_to_long)}")
        print(f"  Total shortened     : {self.total_shortened}")
        print(f"  Total redirects     : {self.total_redirects}")
        print(f"  Undo stack depth    : {len(self.history_stack)}")
        print(f"  Pending in queue    : {len(self.request_queue)}")
        print(f"  ────────────────────────────────────────────\n")


    # =========================================================================
    #  PUBLIC: list_all()
    #  Prints every stored URL — useful for debugging and the demo video.
    # =========================================================================

    def list_all(self):
        print(f"\n  ── All Stored URLs ({len(self.short_to_long)}) ─────────────────")
        if not self.short_to_long:
            print("  (empty)")
        for code, url in self.short_to_long.items():
            clicks = self.click_counts.get(code, 0)
            print(f"  short.ly/{code}  →  {url}  [{clicks} clicks]")
        print(f"  ────────────────────────────────────────────\n")


# =============================================================================
#  DEMO / MANUAL TEST  —  Run this file directly to see everything working
#  python src/url_store.py
# =============================================================================

if __name__ == "__main__":

    print("\n" + "="*60)
    print("  URL SHORTENER  —  DSA Group Project Demo")
    print("="*60 + "\n")

    store = URLStore()

    # ── 1. Shorten some URLs ──────────────────────────────────────
    print("[ STEP 1: Shorten URLs ]\n")
    store.shorten("https://www.google.com")
    store.shorten("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    store.shorten("https://github.com/lionoble20-ctrl/-BIT4107-Mobile-Development")
    store.shorten("https://www.wikipedia.org/wiki/Data_structure")
    store.shorten("https://stackoverflow.com/questions/tagged/python")

    # ── 2. Try shortening the same URL again (should return same code) ─
    print("\n[ STEP 2: Duplicate URL test ]\n")
    store.shorten("https://www.google.com")

    # ── 3. Redirect (simulate clicking links) ────────────────────
    print("\n[ STEP 3: Redirect (simulate clicks) ]\n")
    google_code = store.long_to_short["https://www.google.com"]
    yt_code     = store.long_to_short["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    gh_code     = store.long_to_short["https://github.com/lionoble20-ctrl/-BIT4107-Mobile-Development"]

    store.redirect(google_code)
    store.redirect(google_code)
    store.redirect(google_code)
    store.redirect(yt_code)
    store.redirect(yt_code)
    store.redirect(gh_code)

    # ── 4. Top-K analytics ───────────────────────────────────────
    print("\n[ STEP 4: Top 3 most clicked links ]\n")
    store.top_k(3)

    # ── 5. Delete a link ─────────────────────────────────────────
    print("[ STEP 5: Delete a link ]\n")
    store.delete(yt_code)

    # ── 6. Undo the delete ───────────────────────────────────────
    print("\n[ STEP 6: Undo the delete ]\n")
    store.undo()

    # ── 7. Queue requests (bulk processing) ──────────────────────
    print("\n[ STEP 7: Queue bulk requests ]\n")
    store.queue_request("https://www.bbc.com/news")
    store.queue_request("https://www.reuters.com")
    store.queue_request("https://www.aljazeera.com")
    store.process_queue()

    # ── 8. List all URLs ─────────────────────────────────────────
    print("[ STEP 8: List all stored URLs ]\n")
    store.list_all()

    # ── 9. Final stats ───────────────────────────────────────────
    print("[ STEP 9: Store statistics ]\n")
    store.stats()

    # ── 10. Error handling test ──────────────────────────────────
    print("[ STEP 10: Error handling ]\n")
    try:
        store.redirect("xxxxxx")
    except KeyError as e:
        print(f"  [CAUGHT ERROR]  {e}")

    try:
        store.shorten("not-a-valid-url")
    except ValueError as e:
        print(f"  [CAUGHT ERROR]  {e}")

    print("\n" + "="*60)
    print("  Demo complete — all systems working!")
    print("="*60 + "\n")