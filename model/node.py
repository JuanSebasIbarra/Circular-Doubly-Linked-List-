"""
model/node.py
─────────────
Defines the Node class used by the Circular Doubly Linked List.
Each node stores a single clock tick snapshot.
"""


class Node:
    """
    A single element of the Circular Doubly Linked List.

    Attributes
    ----------
    hour   : int  – 0-23
    minute : int  – 0-59
    second : int  – 0-59
    label  : str  – optional tag, e.g. 'tick', 'lap', 'alarm'
    prev   : Node – reference to the previous node (circular)
    next   : Node – reference to the next node     (circular)
    """

    def __init__(self, hour: int, minute: int, second: int, label: str = "tick"):
        self.hour: int = hour
        self.minute: int = minute
        self.second: int = second
        self.label: str = label
        self.prev: "Node | None" = None
        self.next: "Node | None" = None

    # ── Helpers ──────────────────────────────────────────────────────────────

    def as_tuple(self) -> tuple[int, int, int]:
        """Return (hour, minute, second)."""
        return (self.hour, self.minute, self.second)

    def as_seconds(self) -> int:
        """Convert the stored time to total seconds since midnight."""
        return self.hour * 3600 + self.minute * 60 + self.second

    def formatted(self) -> str:
        """Return a human-readable HH:MM:SS string."""
        return f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}"

    def __repr__(self) -> str:
        return f"Node({self.formatted()} [{self.label}])"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False
        return self.as_tuple() == other.as_tuple()
