# =============================================================================
#  test_all.py  —  Complete Test Suite for the URL Shortening Service
#  DSA-CH23-GROUP-XX  |  Theme B: Bitly-lite
#  Run with: python -m unittest tests/test_all.py -v
# =============================================================================

import unittest
import sys
sys.path.insert(0, './src')
from url_store import URLStore


class TestURLStore(unittest.TestCase):

    def setUp(self):
        """Runs before EVERY test — gives each test a clean empty store."""
        self.store = URLStore()

    # =========================================================================
    #  TESTS 1-3: Shorten
    # =========================================================================

    def test_01_shorten_returns_six_char_code(self):
        """Shortening a URL must return exactly a 6-character code."""
        code = self.store.shorten("https://www.google.com")
        self.assertEqual(len(code), 6, "Short code must be exactly 6 characters")

    def test_02_shorten_same_url_returns_same_code(self):
        """Shortening the same URL twice must return the exact same code."""
        code1 = self.store.shorten("https://www.google.com")
        code2 = self.store.shorten("https://www.google.com")
        self.assertEqual(code1, code2, "Duplicate URL must return same short code")

    def test_03_shorten_different_urls_return_different_codes(self):
        """Two different URLs must never get the same short code."""
        code1 = self.store.shorten("https://www.google.com")
        code2 = self.store.shorten("https://www.youtube.com")
        self.assertNotEqual(code1, code2, "Different URLs must produce different codes")

    # =========================================================================
    #  TESTS 4-6: Redirect
    # =========================================================================

    def test_04_redirect_returns_correct_url(self):
        """Redirecting a short code must return the original long URL."""
        code = self.store.shorten("https://www.google.com")
        result = self.store.redirect(code)
        self.assertEqual(result, "https://www.google.com")

    def test_05_redirect_increments_click_count(self):
        """Every redirect must increase the click count by exactly 1."""
        code = self.store.shorten("https://www.google.com")
        self.store.redirect(code)
        self.store.redirect(code)
        self.store.redirect(code)
        self.assertEqual(self.store.click_counts[code], 3, "Click count must be 3 after 3 redirects")

    def test_06_redirect_nonexistent_code_raises_error(self):
        """Redirecting a code that does not exist must raise a KeyError."""
        with self.assertRaises(KeyError):
            self.store.redirect("xxxxxx")

    # =========================================================================
    #  TESTS 7-8: Delete
    # =========================================================================

    def test_07_delete_removes_url(self):
        """After deleting a short code, redirecting it must raise KeyError."""
        code = self.store.shorten("https://www.google.com")
        self.store.delete(code)
        with self.assertRaises(KeyError):
            self.store.redirect(code)

    def test_08_delete_nonexistent_code_returns_false(self):
        """Deleting a code that does not exist must return False without crashing."""
        result = self.store.delete("xxxxxx")
        self.assertFalse(result, "Deleting a nonexistent code must return False")

    # =========================================================================
    #  TESTS 9-11: Undo (Stack)
    # =========================================================================

    def test_09_undo_restores_deleted_url(self):
        """Undoing a delete must bring the URL back so redirect works again."""
        code = self.store.shorten("https://www.google.com")
        self.store.delete(code)
        self.store.undo()
        result = self.store.redirect(code)
        self.assertEqual(result, "https://www.google.com", "Undo must restore deleted URL")

    def test_10_undo_removes_last_added_url(self):
        """Undoing an add must remove the URL so it can no longer be redirected."""
        code = self.store.shorten("https://www.google.com")
        self.store.undo()
        with self.assertRaises(KeyError):
            self.store.redirect(code)

    def test_11_undo_on_empty_stack_returns_false(self):
        """Calling undo on an empty history stack must return False without crashing."""
        result = self.store.undo()
        self.assertFalse(result, "Undo on empty stack must return False")

    # =========================================================================
    #  TESTS 12-13: Top-K Analytics (Heap)
    # =========================================================================

    def test_12_top_k_returns_correct_order(self):
        """Top-K must return URLs sorted from most clicked to least clicked."""
        code1 = self.store.shorten("https://www.google.com")
        code2 = self.store.shorten("https://www.youtube.com")
        code3 = self.store.shorten("https://www.github.com")

        # Give each URL a different number of clicks
        for _ in range(5): self.store.redirect(code1)  # 5 clicks
        for _ in range(2): self.store.redirect(code2)  # 2 clicks
        for _ in range(8): self.store.redirect(code3)  # 8 clicks

        results = self.store.top_k(3)
        clicks = [r[0] for r in results]

        # Must be in descending order
        self.assertEqual(clicks, sorted(clicks, reverse=True),
                         "Top-K must return results in descending click order")

    def test_13_top_k_when_fewer_urls_than_k(self):
        """Top-K must work correctly even if fewer than K URLs exist in the store."""
        self.store.shorten("https://www.google.com")
        results = self.store.top_k(10)  # ask for 10 but only 1 URL exists
        self.assertEqual(len(results), 1, "Top-K must return only as many as exist")

    # =========================================================================
    #  TESTS 14-15: Queue (Request Buffer)
    # =========================================================================

    def test_14_queue_processes_all_requests(self):
        """All URLs added to the queue must be shortened after process_queue runs."""
        self.store.queue_request("https://www.bbc.com")
        self.store.queue_request("https://www.reuters.com")
        self.store.queue_request("https://www.aljazeera.com")
        self.store.process_queue()
        self.assertEqual(len(self.store.short_to_long), 3,
                         "All 3 queued URLs must be stored after processing")

    def test_15_queue_is_empty_after_processing(self):
        """The request queue must be empty after process_queue runs."""
        self.store.queue_request("https://www.bbc.com")
        self.store.process_queue()
        self.assertEqual(len(self.store.request_queue), 0,
                         "Queue must be empty after processing")

    # =========================================================================
    #  BONUS TESTS (Edge Cases — strengthens your grade)
    # =========================================================================

    def test_16_invalid_url_raises_value_error(self):
        """A URL without http:// or https:// must raise a ValueError."""
        with self.assertRaises(ValueError):
            self.store.shorten("not-a-valid-url")

    def test_17_invalid_url_no_scheme_raises_error(self):
        """A URL starting with www. but missing scheme must raise ValueError."""
        with self.assertRaises(ValueError):
            self.store.shorten("www.google.com")

    def test_18_empty_store_has_zero_urls(self):
        """A freshly created store must have zero URLs stored."""
        self.assertEqual(len(self.store.short_to_long), 0,
                         "New store must start with 0 URLs")

    def test_19_total_redirects_counter_is_accurate(self):
        """The total redirects counter must match exactly how many redirects happened."""
        code = self.store.shorten("https://www.google.com")
        self.store.redirect(code)
        self.store.redirect(code)
        self.assertEqual(self.store.total_redirects, 2,
                         "Total redirects must equal number of redirect calls")

    def test_20_multiple_undos_work_in_sequence(self):
        """Multiple undo operations must each reverse one action correctly."""
        code1 = self.store.shorten("https://www.google.com")
        code2 = self.store.shorten("https://www.youtube.com")

        self.store.undo()  # removes code2
        self.store.undo()  # removes code1

        self.assertEqual(len(self.store.short_to_long), 0,
                         "After 2 undos, store must be empty")


# =============================================================================
#  Run all tests
# =============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)