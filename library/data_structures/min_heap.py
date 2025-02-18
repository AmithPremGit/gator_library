import time

HEAP_SIZE = 20
START_IDX = 1

class HeapNode:
    def __init__(self, patron_id, priority_number, time_of_reservation=None):
        self.patron_id = patron_id
        self.priority_number = priority_number
        self.time_of_reservation = time_of_reservation if time_of_reservation else time.time()

class MinHeap:
    def __init__(self):
        self.length = 0
        self.heap = [None] * (HEAP_SIZE + 1)
    
    def has_higher_priority(self, node1, node2):
        """Compare nodes based on priority first, then time"""
        if node1 is None:
            return False
        if node2 is None:
            return True
            
        # Higher priority number means higher priority (3 > 2 > 1)
        if node1.priority_number != node2.priority_number:
            return node1.priority_number > node2.priority_number
            
        # If same priority, earlier reservation time wins
        return node1.time_of_reservation < node2.time_of_reservation
    
    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def insert(self, patron_id, priority_number, time_of_reservation=None):
        """Insert new reservation into heap"""
        if self.length >= HEAP_SIZE:
            return False
        
        self.length += 1
        new_node = HeapNode(patron_id, priority_number, time_of_reservation)
        self.heap[self.length] = new_node
        
        # Bubble up
        current_idx = self.length
        while current_idx > 1:
            parent_idx = current_idx // 2
            if self.has_higher_priority(self.heap[current_idx], self.heap[parent_idx]):
                self.swap(current_idx, parent_idx)
                current_idx = parent_idx
            else:
                break
                
        return True

    def delete(self):
        """Remove and return highest priority reservation"""
        if self.length == 0:
            return None
            
        highest_priority = self.heap[START_IDX]
        self.heap[START_IDX] = self.heap[self.length]
        self.length -= 1
        
        if self.length > 0:
            self._heapify(START_IDX)
            
        return highest_priority
    
    def _heapify(self, idx):
        """Maintain heap property starting from idx"""
        largest = idx
        left = 2 * idx
        right = 2 * idx + 1
        
        # Find highest priority among parent and children
        if left <= self.length and self.has_higher_priority(self.heap[left], self.heap[largest]):
            largest = left
            
        if right <= self.length and self.has_higher_priority(self.heap[right], self.heap[largest]):
            largest = right
            
        # If highest priority is not the parent, swap and continue heapifying
        if largest != idx:
            self.swap(idx, largest)
            self._heapify(largest)

    def get_size(self):
        """Return current number of reservations"""
        return self.length