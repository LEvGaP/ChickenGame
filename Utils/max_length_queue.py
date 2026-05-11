from collections import deque


class MaxLengthQueue:
    def __init__(self, max_length):
        """
        Initialize a queue with maximum length.

        Args:
            max_length: Maximum number of elements the queue can hold
        """
        if max_length <= 0:
            raise ValueError("Max length must be positive")
        self.max_length = max_length
        self.queue = deque(maxlen=max_length)

    def enqueue(self, item):
        """
        Add an item to the rear of the queue.
        If queue is at max length, the front item is automatically removed.

        Args:
            item: Item to add to the queue
        """
        self.queue.append(item)

    def dequeue(self):
        """
        Remove and return the front item from the queue.

        Returns:
            The front item, or None if queue is empty
        """
        if self.is_empty():
            return None
        return self.queue.popleft()

    def peek(self):
        """
        Return the front item without removing it.

        Returns:
            The front item, or None if queue is empty
        """
        if self.is_empty():
            return None
        return self.queue[0]

    def is_empty(self):
        """Check if the queue is empty."""
        return len(self.queue) == 0

    def is_full(self):
        """Check if the queue is at maximum capacity."""
        return len(self.queue) == self.max_length

    def size(self):
        """Return the current number of items in the queue."""
        return len(self.queue)

    def clear(self):
        """Remove all items from the queue."""
        self.queue.clear()

    def __str__(self):
        """String representation of the queue."""
        return f"Queue({list(self.queue)})"

    def __len__(self):
        """Return the current size of the queue."""
        return len(self.queue)
