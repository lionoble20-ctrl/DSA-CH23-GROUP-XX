# =============================================================================
#  sorter.py  —  Sorting & Searching for the URL Shortening Service
#  DSA-CH23-GROUP-XX  |  Theme B: Bitly-lite
#  Algorithms Used: Merge Sort O(n log n), Binary Search O(log n)
# =============================================================================
#
#  WHAT THIS FILE DOES:
#  - Sorts URLs by click count using Merge Sort
#  - Searches for URLs above a click threshold using Binary Search
#  - Both algorithms are required by the assignment
#
# =============================================================================


# =============================================================================
#  merge_sort(data)
#  Sorts a list of (click_count, short_code, long_url) tuples by click count
#  Big-O: O(n log n) time  |  O(n) space
# =============================================================================

def merge_sort(data: list) -> list:
    if len(data) <= 1:
        return data

    # Split list in half
    mid   = len(data) // 2
    left  = merge_sort(data[:mid])
    right = merge_sort(data[mid:])

    return _merge(left, right)


def _merge(left: list, right: list) -> list:
    result = []
    i = j  = 0

    while i < len(left) and j < len(right):
        # Sort descending by click count (index 0 of each tuple)
        if left[i][0] >= right[j][0]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append any remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# =============================================================================
#  binary_search_threshold(sorted_data, threshold)
#  Finds the index where click counts drop below a threshold
#  Input must be sorted in DESCENDING order (use merge_sort first)
#  Returns a list of all URLs with clicks >= threshold
#  Big-O: O(log n)
# =============================================================================

def binary_search_threshold(sorted_data: list, threshold: int) -> list:
    low  = 0
    high = len(sorted_data) - 1
    result_index = len(sorted_data)  # default: nothing meets threshold

    while low <= high:
        mid = (low + high) // 2
        if sorted_data[mid][0] >= threshold:
            result_index = mid
            low = mid + 1  # look further right (descending order)
        else:
            high = mid - 1

    return sorted_data[:result_index + 1]


# =============================================================================
#  sort_urls_by_clicks(url_store)
#  Takes a URLStore object and returns all URLs sorted by click count
#  This is the main function your main.py will call
# =============================================================================

def sort_urls_by_clicks(url_store) -> list:
    data = []
    for code, url in url_store.short_to_long.items():
        clicks = url_store.click_counts.get(code, 0)
        data.append((clicks, code, url))

    sorted_data = merge_sort(data)

    print(f"\n  ── URLs Sorted by Click Count (Merge Sort) ──")
    for rank, (clicks, code, url) in enumerate(sorted_data, 1):
        print(f"  #{rank}  [{clicks} clicks]  short.ly/{code}  →  {url}")
    print(f"  ────────────────────────────────────────────\n")

    return sorted_data


# =============================================================================
#  DEMO — Run directly: python src/sorter.py
# =============================================================================

if __name__ == "__main__":

    print("\n" + "="*60)
    print("  SORTER  —  Merge Sort + Binary Search Demo")
    print("="*60 + "\n")

    # Sample data: (click_count, short_code, long_url)
    sample_data = [
        (3,  "abc123", "https://www.google.com"),
        (15, "def456", "https://www.youtube.com"),
        (1,  "ghi789", "https://www.wikipedia.org"),
        (9,  "jkl012", "https://www.github.com"),
        (6,  "mno345", "https://www.stackoverflow.com"),
        (22, "pqr678", "https://www.reddit.com"),
        (4,  "stu901", "https://www.bbc.com"),
    ]

    print("[ Unsorted data ]\n")
    for item in sample_data:
        print(f"  {item[1]}  →  {item[2]}  [{item[0]} clicks]")

    print("\n[ After Merge Sort (descending by clicks) ]\n")
    sorted_data = merge_sort(sample_data)
    for rank, (clicks, code, url) in enumerate(sorted_data, 1):
        print(f"  #{rank}  [{clicks} clicks]  short.ly/{code}  →  {url}")

    print("\n[ Binary Search: URLs with 5 or more clicks ]\n")
    results = binary_search_threshold(sorted_data, 5)
    for clicks, code, url in results:
        print(f"  [{clicks} clicks]  short.ly/{code}  →  {url}")

    print(f"\n  Found {len(results)} URLs with 5+ clicks out of {len(sorted_data)} total")

    print("\n" + "="*60)
    print("  Sorter demo complete!")
    print("="*60 + "\n")