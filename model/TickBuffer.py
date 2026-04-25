"""
model/circular_doubly_linked_list.py
─────────────────────────────────────
Circular Doubly Linked List (CDLL) tailored for clock operations.

Clock-related CDLL functionalities demonstrated
────────────────────────────────────────────────
1.  append()         – Add a new time-tick at the tail (O(1))
2.  prepend()        – Add a new time-tick at the head  (O(1))
3.  delete_node()    – Remove any node by reference     (O(1))
4.  search()         – Find a node matching HH:MM:SS    (O(n))
5.  latest()         – Retrieve the most recent tick    (O(1))
6.  oldest()         – Retrieve the oldest stored tick  (O(1))
7.  traverse_forward()  – Iterate oldest → newest       (O(n))
8.  traverse_backward() – Iterate newest → oldest       (O(n))
9.  get_laps()       – Filter nodes labelled 'lap'      (O(n))
10. get_alarms()     – Filter nodes labelled 'alarm'    (O(n))
11. count()          – Total nodes in the list           (O(1))
12. clear()          – Wipe the entire list              (O(1))
13. evict_oldest()   – Auto-remove oldest when at capacity (O(1))
"""

from __future__ import annotations
from typing import Generator, Optional
from .node import Node


class CircularDoublyLinkedList:
    """
    A capacity-bounded Circular Doubly Linked List.

    Parameters
    ----------
    capacity : int
        Maximum number of nodes to keep. When exceeded, the oldest node
        is automatically evicted (FIFO policy). Default is 60 (1 minute
        of per-second ticks).
    """

    def __init__(self, capacity: int = 60) -> None:
        self._head: Optional[Node] = None
        self._size: int = 0
        self.capacity: int = capacity

    # ── 11. count ──────────────────────────────────────────────────────────────
    @property
    def size(self) -> int:
        """Total number of nodes currently stored."""
        return self._size

    def is_empty(self) -> bool:
        return self._head is None

    # ── 1. append ─────────────────────────────────────────────────────────────
    def append(self, hour: int, minute: int, second: int,
               label: str = "tick") -> Node:
        """
        Insert a new node at the TAIL of the list.
        Auto-evicts the oldest node when capacity is reached.
        """
        new_node = Node(hour, minute, second, label)
        if self._head is None:
            new_node.next = new_node
            new_node.prev = new_node
            self._head = new_node
        else:
            tail = self._head.prev          # O(1) — tail is always head.prev
            tail.next = new_node
            new_node.prev = tail
            new_node.next = self._head
            self._head.prev = new_node

        self._size += 1

        # 13. evict_oldest — auto-evict when over capacity
        if self._size > self.capacity:
            self._evict_oldest()

        return new_node

    # ── 2. prepend ────────────────────────────────────────────────────────────
    def prepend(self, hour: int, minute: int, second: int,
                label: str = "tick") -> Node:
        """Insert a new node at the HEAD of the list."""
        new_node = Node(hour, minute, second, label)
        if self._head is None:
            new_node.next = new_node
            new_node.prev = new_node
        else:
            tail = self._head.prev
            new_node.next = self._head
            new_node.prev = tail
            tail.next = new_node
            self._head.prev = new_node

        self._head = new_node
        self._size += 1

        if self._size > self.capacity:
            self._evict_oldest()

        return new_node

    # ── 3. delete_node ────────────────────────────────────────────────────────
    def delete_node(self, node: Node) -> bool:
        """
        Remove *node* from the list in O(1).
        Returns True if successful, False if the list is empty.
        """
        if self._head is None:
            return False

        if self._size == 1:
            self._head = None
            self._size = 0
            return True

        node.prev.next = node.next
        node.next.prev = node.prev

        if node is self._head:
            self._head = node.next

        self._size -= 1
        return True

    # ── 4. search ─────────────────────────────────────────────────────────────
    def search(self, hour: int, minute: int, second: int) -> Optional[Node]:
        """
        Find the first node whose time matches (hour, minute, second).
        Returns the Node or None if not found. O(n).
        """
        for node in self.traverse_forward():
            if node.hour == hour and node.minute == minute and node.second == second:
                return node
        return None

    # ── 5. latest ─────────────────────────────────────────────────────────────
    def latest(self) -> Optional[Node]:
        """Return the most recently appended node (tail). O(1)."""
        return self._head.prev if self._head else None

    # ── 6. oldest ─────────────────────────────────────────────────────────────
    def oldest(self) -> Optional[Node]:
        """Return the oldest stored node (head). O(1)."""
        return self._head

    # ── 7. traverse_forward ───────────────────────────────────────────────────
    def traverse_forward(self) -> Generator[Node, None, None]:
        """Yield every node from oldest (head) to newest (tail)."""
        if self._head is None:
            return
        current = self._head
        while True:
            yield current
            current = current.next
            if current is self._head:
                break

    # ── 8. traverse_backward ──────────────────────────────────────────────────
    def traverse_backward(self) -> Generator[Node, None, None]:
        """Yield every node from newest (tail) to oldest (head)."""
        if self._head is None:
            return
        current = self._head.prev   # start at tail
        while True:
            yield current
            current = current.prev
            if current is self._head.prev:
                break

    # ── 9. get_laps ───────────────────────────────────────────────────────────
    def get_laps(self) -> list[Node]:
        """Return all nodes labelled 'lap', in insertion order."""
        return [n for n in self.traverse_forward() if n.label == "lap"]

    # ── 10. get_alarms ────────────────────────────────────────────────────────
    def get_alarms(self) -> list[Node]:
        """Return all nodes labelled 'alarm', in insertion order."""
        return [n for n in self.traverse_forward() if n.label == "alarm"]

    # ── 12. clear ─────────────────────────────────────────────────────────────
    def clear(self) -> None:
        """Remove all nodes from the list."""
        self._head = None
        self._size = 0

    # ── 13. evict_oldest (internal) ───────────────────────────────────────────
    def _evict_oldest(self) -> None:
        """Remove the head (oldest) node. O(1)."""
        if self._size <= 1:
            self.clear()
            return
        oldest = self._head
        self._head = oldest.next
        self._head.prev = oldest.prev
        oldest.prev.next = self._head
        self._size -= 1

    # ── Dunder helpers ────────────────────────────────────────────────────────
    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        nodes = list(self.traverse_forward())
        body = " ⇄ ".join(str(n) for n in nodes)
        return f"CDLL(size={self._size}/{self.capacity}) [{body}]"
