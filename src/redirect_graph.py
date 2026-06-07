# =============================================================================
#  redirect_graph.py  —  Redirect Chain Graph with BFS/DFS
#  DSA-CH23-GROUP-XX  |  Theme B: Bitly-lite
#  Data Structures Used: Graph (Adjacency List), BFS, DFS
# =============================================================================
#
#  WHAT THIS FILE DOES:
#  Models redirect chains — e.g. short.ly/abc → short.ly/xyz → final URL
#  Uses BFS to find the shortest redirect path
#  Uses DFS to detect redirect loops (A → B → C → A = infinite loop = bad)
#
# =============================================================================

from collections import deque


class RedirectGraph:

    def __init__(self):
        # Adjacency list — each node is a short code or URL
        # { "abc123": "xyz789" } means abc123 redirects to xyz789
        self.graph = {}


    # =========================================================================
    #  add_redirect(from_code, to_code)
    #  Adds a directed edge: from_code → to_code
    #  Big-O: O(1)
    # =========================================================================

    def add_redirect(self, from_code: str, to_code: str):
        self.graph[from_code] = to_code
        print(f"  [GRAPH]  Added redirect: {from_code} → {to_code}")


    # =========================================================================
    #  remove_redirect(from_code)
    #  Removes a redirect edge
    #  Big-O: O(1)
    # =========================================================================

    def remove_redirect(self, from_code: str):
        if from_code in self.graph:
            del self.graph[from_code]
            print(f"  [GRAPH]  Removed redirect: {from_code}")
        else:
            print(f"  [GRAPH]  '{from_code}' not found in graph")


    # =========================================================================
    #  bfs_path(start)
    #  Uses BFS to find the full redirect chain from a starting code
    #  Returns the list of nodes visited in order
    #  Big-O: O(V + E) where V = nodes, E = edges
    # =========================================================================

    def bfs_path(self, start: str) -> list:
        if start not in self.graph:
            print(f"  [BFS]  '{start}' has no outgoing redirects")
            return [start]

        visited = set()
        queue   = deque([start])
        path    = []

        print(f"\n  ── BFS Redirect Path from '{start}' ──────────")

        while queue:
            node = queue.popleft()

            if node in visited:
                print(f"  [BFS]  Loop detected at '{node}' — stopping")
                break

            visited.add(node)
            path.append(node)
            print(f"  [BFS]  Visiting: {node}")

            # Follow the redirect if one exists
            if node in self.graph:
                next_node = self.graph[node]
                queue.append(next_node)

        print(f"  Full path: {' → '.join(path)}")
        print(f"  ────────────────────────────────────────────\n")
        return path


    # =========================================================================
    #  dfs_detect_loop(start)
    #  Uses DFS to detect if a redirect chain contains a loop
    #  Returns True if a loop is found, False if the chain is clean
    #  Big-O: O(V + E)
    # =========================================================================

    def dfs_detect_loop(self, start: str) -> bool:
        visited    = set()
        rec_stack  = set()  # tracks nodes in current DFS path

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)

            if node in self.graph:
                neighbour = self.graph[node]
                if neighbour not in visited:
                    if dfs(neighbour):
                        return True
                elif neighbour in rec_stack:
                    # Found a back edge — this is a loop
                    print(f"  [DFS]  ⚠ Loop detected: '{neighbour}' appears twice in path")
                    return True

            rec_stack.remove(node)
            return False

        result = dfs(start)
        if not result:
            print(f"  [DFS]  ✓ No loop detected from '{start}' — chain is clean")
        return result


    # =========================================================================
    #  get_final_destination(start)
    #  Follows a redirect chain all the way to the end (no more redirects)
    #  Stops if a loop is detected
    #  Big-O: O(n) where n = chain length
    # =========================================================================

    def get_final_destination(self, start: str) -> str:
        visited = set()
        current = start

        while current in self.graph:
            if current in visited:
                print(f"  [CHAIN]  Loop detected at '{current}' — cannot resolve final destination")
                return current
            visited.add(current)
            current = self.graph[current]

        print(f"  [CHAIN]  Final destination from '{start}': {current}")
        return current


    # =========================================================================
    #  show_graph()
    #  Prints the entire graph — useful for debugging and demo video
    # =========================================================================

    def show_graph(self):
        print(f"\n  ── Redirect Graph ({len(self.graph)} edges) ──────────────")
        if not self.graph:
            print("  (empty)")
        for src, dst in self.graph.items():
            print(f"  {src}  →  {dst}")
        print(f"  ────────────────────────────────────────────\n")


# =============================================================================
#  DEMO — Run directly: python src/redirect_graph.py
# =============================================================================

if __name__ == "__main__":

    print("\n" + "="*60)
    print("  REDIRECT GRAPH  —  BFS / DFS Demo")
    print("="*60 + "\n")

    g = RedirectGraph()

    # Build a redirect chain: abc → def → ghi → final
    print("[ Building redirect chain ]\n")
    g.add_redirect("abc123", "def456")
    g.add_redirect("def456", "ghi789")
    g.add_redirect("ghi789", "https://www.google.com")

    g.show_graph()

    # BFS — follow the path
    print("[ BFS: Follow redirect chain from abc123 ]")
    g.bfs_path("abc123")

    # DFS — check for loops (clean chain)
    print("[ DFS: Check for loops — clean chain ]")
    g.dfs_detect_loop("abc123")

    # Get final destination
    print("\n[ Final destination ]")
    g.get_final_destination("abc123")

    # Now create a loop: xyz → pqr → xyz (loop!)
    print("\n[ Creating a redirect loop for testing ]\n")
    g.add_redirect("xyz111", "pqr222")
    g.add_redirect("pqr222", "xyz111")  # loop back!

    print("\n[ DFS: Check for loops — loop chain ]")
    g.dfs_detect_loop("xyz111")

    print("\n[ BFS: Follow looped chain — should stop ]\n")
    g.bfs_path("xyz111")

    print("="*60)
    print("  Redirect Graph demo complete!")
    print("="*60 + "\n")