# =============================================================================
#  main.py  —  CLI Entry Point for the URL Shortening Service
#  DSA-CH23-GROUP-XX  |  Theme B: Bitly-lite
#  Run with: python src/main.py
# =============================================================================

import sys
sys.path.insert(0, './src')

from url_store       import URLStore
from redirect_graph  import RedirectGraph
from sorter          import sort_urls_by_clicks, binary_search_threshold, merge_sort


# =============================================================================
#  Setup — create global instances
# =============================================================================

store = URLStore()
graph = RedirectGraph()


# =============================================================================
#  Menu display
# =============================================================================

def print_menu():
    print("\n" + "="*55)
    print("   URL SHORTENER  —  DSA Group Project")
    print("="*55)
    print("  [1]  Shorten a URL")
    print("  [2]  Redirect (visit a short link)")
    print("  [3]  Delete a short link")
    print("  [4]  Undo last action")
    print("  [5]  View top-K most clicked links")
    print("  [6]  Sort all URLs by click count")
    print("  [7]  Search URLs above click threshold")
    print("  [8]  Add a redirect chain (Graph)")
    print("  [9]  Check redirect chain for loops (DFS)")
    print("  [10] Follow redirect chain (BFS)")
    print("  [11] List all stored URLs")
    print("  [12] View store statistics")
    print("  [0]  Exit")
    print("="*55)


# =============================================================================
#  Handlers for each menu option
# =============================================================================

def handle_shorten():
    url = input("\n  Enter long URL: ").strip()
    try:
        code = store.shorten(url)
        print(f"\n  ✓ Short link created: short.ly/{code}")
    except ValueError as e:
        print(f"\n  ✗ Error: {e}")


def handle_redirect():
    code = input("\n  Enter short code (e.g. 8ffdef): ").strip()
    try:
        url = store.redirect(code)
        print(f"\n  ✓ Redirecting to: {url}")
    except KeyError as e:
        print(f"\n  ✗ Error: {e}")


def handle_delete():
    code = input("\n  Enter short code to delete: ").strip()
    result = store.delete(code)
    if result:
        print(f"\n  ✓ Deleted short.ly/{code}")


def handle_undo():
    store.undo()


def handle_top_k():
    try:
        k = int(input("\n  How many top links to show? (e.g. 5): ").strip())
        store.top_k(k)
    except ValueError:
        print("\n  ✗ Please enter a valid number")


def handle_sort():
    if not store.short_to_long:
        print("\n  No URLs stored yet.")
        return
    sort_urls_by_clicks(store)


def handle_search_threshold():
    if not store.short_to_long:
        print("\n  No URLs stored yet.")
        return
    try:
        threshold = int(input("\n  Show URLs with at least how many clicks? ").strip())
        data = [(store.click_counts.get(c, 0), c, u)
                for c, u in store.short_to_long.items()]
        sorted_data = merge_sort(data)
        results = binary_search_threshold(sorted_data, threshold)
        print(f"\n  URLs with {threshold}+ clicks:")
        if not results:
            print("  None found.")
        for clicks, code, url in results:
            print(f"  [{clicks} clicks]  short.ly/{code}  →  {url}")
    except ValueError:
        print("\n  ✗ Please enter a valid number")


def handle_add_redirect():
    print("\n  Add a redirect chain entry")
    from_code = input("  From short code: ").strip()
    to_code   = input("  To short code or URL: ").strip()
    graph.add_redirect(from_code, to_code)


def handle_check_loop():
    code = input("\n  Enter starting short code to check for loops: ").strip()
    has_loop = graph.dfs_detect_loop(code)
    if has_loop:
        print(f"\n  ⚠ WARNING: Loop detected in redirect chain from '{code}'")
    else:
        print(f"\n  ✓ No loop — redirect chain from '{code}' is clean")


def handle_bfs():
    code = input("\n  Enter starting short code to follow redirect chain: ").strip()
    graph.bfs_path(code)


def handle_list_all():
    store.list_all()


def handle_stats():
    store.stats()


# =============================================================================
#  MAIN LOOP
# =============================================================================

def main():
    print("\n  Welcome to the URL Shortener — DSA Group Project")
    print("  Type a number and press Enter to choose an option\n")

    # Pre-load some sample data so the demo video has content
    print("  Loading sample data...\n")
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        c1 = store.shorten("https://www.google.com")
        c2 = store.shorten("https://www.youtube.com")
        c3 = store.shorten("https://www.github.com")
        c4 = store.shorten("https://www.wikipedia.org")
        c5 = store.shorten("https://www.stackoverflow.com")
        for _ in range(5): store.redirect(c1)
        for _ in range(3): store.redirect(c2)
        for _ in range(8): store.redirect(c3)
        for _ in range(1): store.redirect(c4)
        graph.add_redirect(c1, c2)
        graph.add_redirect(c2, c3)

    print("  ✓ 5 sample URLs loaded with click data\n")

    while True:
        print_menu()
        choice = input("\n  Enter your choice: ").strip()

        if   choice == "1":  handle_shorten()
        elif choice == "2":  handle_redirect()
        elif choice == "3":  handle_delete()
        elif choice == "4":  handle_undo()
        elif choice == "5":  handle_top_k()
        elif choice == "6":  handle_sort()
        elif choice == "7":  handle_search_threshold()
        elif choice == "8":  handle_add_redirect()
        elif choice == "9":  handle_check_loop()
        elif choice == "10": handle_bfs()
        elif choice == "11": handle_list_all()
        elif choice == "12": handle_stats()
        elif choice == "0":
            print("\n  Goodbye! — DSA Group Project\n")
            break
        else:
            print("\n  ✗ Invalid choice — please enter a number from the menu")


if __name__ == "__main__":
    main()