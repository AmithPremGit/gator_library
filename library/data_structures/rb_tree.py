from .min_heap import MinHeap, HeapNode

class Node:
    def __init__(self, book_id, title, author, availability_status="Yes"):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.availability_status = availability_status
        self.color = "red"  # New nodes are always red
        self.left = None
        self.right = None
        self.parent = None
        self.borrowed_by = None
        self.reservation_heap = MinHeap()  # Using MinHeap for reservations

class GatorLibrary:
    def __init__(self):
        # Create the sentinel NIL node
        self.nil = Node(None, None, None)
        self.nil.color = "black"
        # Initialize root as NIL
        self.root = self.nil
        # Counter for color flips
        self.color_flip_count = 0

    def _fix_insert(self, node):
        """Fix Red-Black Tree violations after insertion"""
        # Keep going up while there's a red-red violation
        current = node  # Keep track of the node we're working with
        
        while current != self.root and current.parent.color == "red":
            # If parent is a left child
            if current.parent == current.parent.parent.left:
                uncle = current.parent.parent.right
                
                # Case 1: Uncle is red - recolor only
                if uncle != self.nil and uncle.color == "red":
                    self._change_color(current.parent, "black")
                    self._change_color(uncle, "black")
                    self._change_color(current.parent.parent, "red")
                    current = current.parent.parent
                else:
                    # Case 2: Node is right child - need left rotation
                    if current == current.parent.right:
                        current = current.parent
                        self._left_rotate(current)
                    # Case 3: Node is left child - need right rotation
                    self._change_color(current.parent, "black")
                    self._change_color(current.parent.parent, "red")
                    self._right_rotate(current.parent.parent)
            # If parent is a right child (mirror cases)
            else:
                uncle = current.parent.parent.left
                
                # Case 1: Uncle is red - recolor only
                if uncle != self.nil and uncle.color == "red":
                    self._change_color(current.parent, "black")
                    self._change_color(uncle, "black")
                    self._change_color(current.parent.parent, "red")
                    current = current.parent.parent
                else:
                    # Case 2: Node is left child - need right rotation
                    if current == current.parent.left:
                        current = current.parent
                        self._right_rotate(current)
                    # Case 3: Node is right child - need left rotation
                    self._change_color(current.parent, "black")
                    self._change_color(current.parent.parent, "red")
                    self._left_rotate(current.parent.parent)
        
        # Ensure root is black
        self._change_color(self.root, "black")
        
        # Return the original node that was inserted
        return node  # Important: return the original node, not current

    def _left_rotate(self, x):
        """Perform left rotation"""
        y = x.right
        
        # Turn y's left subtree into x's right subtree
        x.right = y.left
        if y.left != self.nil:
            y.left.parent = x

        # Link x's parent to y
        y.parent = x.parent
        if x.parent == self.nil:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        # Put x on y's left
        y.left = x
        x.parent = y

    def _right_rotate(self, x):
        """Perform right rotation"""
        y = x.left
        
        # Turn y's right subtree into x's left subtree
        x.left = y.right
        if y.right != self.nil:
            y.right.parent = x

        # Link x's parent to y
        y.parent = x.parent
        if x.parent == self.nil:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y

        # Put x on y's right
        y.right = x
        x.parent = y

    def _change_color(self, node, new_color):
        """Helper method to change node color and track flips"""
        if node != self.nil and node.color != new_color:
            print(f"DEBUG: Changing color of node {node.book_id} from {node.color} to {new_color}")
            node.color = new_color
            self.color_flip_count += 1
            return True
        return False

    def insert_book(self, book_id, title, author, availability_status="Yes"):
        """Insert a new book into the Red-Black Tree"""
        print(f"DEBUG: Starting insertion of book {book_id}")
        new_node = Node(book_id, title, author, availability_status)
        new_node.left = self.nil
        new_node.right = self.nil
        new_node.parent = self.nil
        new_node.color = "red"  # New nodes start red
        
        # Standard BST insertion
        parent = self.nil
        current = self.root
        
        while current != self.nil:
            parent = current
            if book_id < current.book_id:
                current = current.left
            else:
                current = current.right
        
        new_node.parent = parent
        
        if parent == self.nil:
            self.root = new_node
            print("DEBUG: Inserted as root node")
        elif book_id < parent.book_id:
            parent.left = new_node
            print(f"DEBUG: Inserted as left child of {parent.book_id}")
        else:
            parent.right = new_node
            print(f"DEBUG: Inserted as right child of {parent.book_id}")
        
        # Fix the tree and get the final node
        fixed_node = self._fix_insert(new_node)
        print(f"DEBUG: Insertion complete. Node {book_id} final color: {fixed_node.color}")
        
        return fixed_node

    def find_node(self, book_id):
        """Find a node by book_id"""
        current = self.root
        while current != self.nil:
            if book_id == current.book_id:
                return current
            elif book_id < current.book_id:
                current = current.left
            else:
                current = current.right
        return None

    def borrow_book(self, patron_id, book_id, priority=1):
        """Borrow a book or add to reservation heap"""
        node = self.find_node(book_id)
        if not node:
            return False, "Book not found"
        
        if node.availability_status == "No":
            # Add to reservation heap
            success = node.reservation_heap.insert(patron_id, priority)
            if not success:
                return False, "Reservation list is full"
            return False, "Book is currently borrowed. Added to reservation list."
        
        node.availability_status = "No"
        node.borrowed_by = patron_id
        return True, "Book borrowed successfully"

    def return_book(self, patron_id, book_id):
        """Return a book and handle reservations"""
        node = self.find_node(book_id)
        if not node:
            return False, "Book not found"
        
        if node.borrowed_by != patron_id:
            return False, "Book was not borrowed by this patron"
        
        # Check reservation heap for next patron
        next_reservation = node.reservation_heap.delete()
        if next_reservation:
            # Allocate to the highest priority reservation
            node.borrowed_by = next_reservation.patron_id
            return True, f"Book returned and allocated to patron {next_reservation.patron_id}"
        
        # No reservations, mark as available
        node.availability_status = "Yes"
        node.borrowed_by = None
        return True, "Book returned successfully"

    def _transplant(self, u, v):
        """Helper for deletion - transplant subtree v at node u"""
        if u.parent == self.nil:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def _minimum(self, node):
        """Find the minimum value in a subtree"""
        current = node
        while current.left != self.nil:
            current = current.left
        return current

    def delete_book(self, book_id):
        """Delete a book and return list of cancelled reservations"""
        z = self.find_node(book_id)
        if not z:
            return []
        
        # Get all reservations from heap
        cancelled_reservations = []
        while True:
            reservation = z.reservation_heap.delete()
            if not reservation:
                break
            cancelled_reservations.append(reservation.patron_id)
        
        # Perform the deletion
        y = z
        y_original_color = y.color
        
        if z.left == self.nil:
            x = z.right
            self._transplant(z, z.right)
        elif z.right == self.nil:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            
            if y.parent == z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        
        if y_original_color == "black":
            self._fix_delete(x)
            
        return cancelled_reservations

    def _fix_delete(self, x):
        """Fix Red-Black Tree violations after deletion"""
        while x != self.root and x.color == "black":
            if x == x.parent.left:
                w = x.parent.right
                
                # Case 1: Brother is red
                if w.color == "red":
                    self._change_color(w, "black")
                    self._change_color(x.parent, "red")
                    self._left_rotate(x.parent)
                    w = x.parent.right
                
                # Case 2: Brother is black with two black children
                if w.left.color == "black" and w.right.color == "black":
                    self._change_color(w, "red")
                    x = x.parent
                else:
                    # Case 3: Brother is black with red left child
                    if w.right.color == "black":
                        self._change_color(w.left, "black")
                        self._change_color(w, "red")
                        self._right_rotate(w)
                        w = x.parent.right
                    
                    # Case 4: Brother is black with red right child
                    self._change_color(w, x.parent.color)
                    self._change_color(x.parent, "black")
                    self._change_color(w.right, "black")
                    self._left_rotate(x.parent)
                    x = self.root
            else:
                # Mirror cases for right child
                w = x.parent.left
                
                if w.color == "red":
                    self._change_color(w, "black")
                    self._change_color(x.parent, "red")
                    self._right_rotate(x.parent)
                    w = x.parent.left
                
                if w.right.color == "black" and w.left.color == "black":
                    self._change_color(w, "red")
                    x = x.parent
                else:
                    if w.left.color == "black":
                        self._change_color(w.right, "black")
                        self._change_color(w, "red")
                        self._left_rotate(w)
                        w = x.parent.left
                    
                    self._change_color(w, x.parent.color)
                    self._change_color(x.parent, "black")
                    self._change_color(w.left, "black")
                    self._right_rotate(x.parent)
                    x = self.root
        
        self._change_color(x, "black")

    def find_closest_book(self, target_id):
        """Find the book with ID closest to target_id"""
        closest = None
        min_diff = float('inf')
        
        def inorder_traverse(node):
            nonlocal closest, min_diff
            if node == self.nil:
                return
            
            inorder_traverse(node.left)
            
            diff = abs(node.book_id - target_id)
            if diff < min_diff:
                min_diff = diff
                closest = node
            
            inorder_traverse(node.right)
        
        inorder_traverse(self.root)
        return closest

    def get_color_flip_count(self):
        """Return the total number of color flips performed"""
        return self.color_flip_count