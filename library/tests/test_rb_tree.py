from django.test import TestCase
from library.data_structures.rb_tree import GatorLibrary
from library.data_structures.min_heap import MinHeap, HeapNode, HEAP_SIZE

class RBTreeTests(TestCase):
    def setUp(self):
        self.tree = GatorLibrary()

    def print_tree(self, node, level=0, prefix="Root: "):
        """Helper method to print tree structure for debugging"""
        if node == self.tree.nil:
            return "NIL\n"
        
        result = []
        result.append("  " * level + prefix + f"{node.book_id}\n")
        
        if node.left != self.tree.nil:
            result.append(self.print_tree(node.left, level + 1, "L--- "))
        else:
            result.append("  " * (level + 1) + "L--- NIL\n")
            
        if node.right != self.tree.nil:
            result.append(self.print_tree(node.right, level + 1, "R--- "))
        else:
            result.append("  " * (level + 1) + "R--- NIL\n")
            
        return "".join(result)

    def verify_rb_properties(self, node=None):
        """Verify Red-Black tree properties with detailed error messages"""
        if node is None:
            if self.tree.root == self.tree.nil:
                return True, "Tree is empty"
                
            # No need to verify root color since it's an internal detail
            return self.verify_rb_properties(self.tree.root)

        # Property 4: Parent pointers must be correct
        if node.left != self.tree.nil and node.left.parent != node:
            tree_state = self.print_tree(self.tree.root)
            return False, f"Property 4 violation: Incorrect parent pointer for left child of {node.book_id}\nTree state:\n{tree_state}"
            
        if node.right != self.tree.nil and node.right.parent != node:
            tree_state = self.print_tree(self.tree.root)
            return False, f"Property 4 violation: Incorrect parent pointer for right child of {node.book_id}\nTree state:\n{tree_state}"

        # Recursively verify children
        if node.left != self.tree.nil:
            result, message = self.verify_rb_properties(node.left)
            if not result:
                return False, message

        if node.right != self.tree.nil:
            result, message = self.verify_rb_properties(node.right)
            if not result:
                return False, message

        return True, "All properties verified"

    def test_insertion_maintains_rb_properties(self):
        """Test that inserting nodes maintains RB tree properties"""
        books = [
            (1, "Book 1", "Author 1"),
            (3, "Book 3", "Author 3"),
            (5, "Book 5", "Author 5"),
            (7, "Book 7", "Author 7"),
            (2, "Book 2", "Author 2"),
            (4, "Book 4", "Author 4"),
            (6, "Book 6", "Author 6"),
        ]
        
        for i, (book_id, title, author) in enumerate(books, 1):
            print(f"\nTest case {i}: Inserting book {book_id}")
            
            if self.tree.root != self.tree.nil:
                print("Tree before insertion:")
                print(self.print_tree(self.tree.root))
            
            node = self.tree.insert_book(book_id, title, author)
            
            print("Tree after insertion:")
            print(self.print_tree(self.tree.root))
            
            result, message = self.verify_rb_properties()
            self.assertTrue(result, f"RB tree properties violated after inserting book {book_id}:\n{message}")
            
            self.assertIsInstance(node.reservation_heap, MinHeap, 
                                "Node should have a MinHeap for reservations")

    def test_deletion_maintains_rb_properties(self):
        """Test that deleting nodes maintains RB tree properties"""
        # First insert some books
        books = [(i, f"Book {i}", f"Author {i}") for i in range(1, 8)]
        for book_id, title, author in books:
            self.tree.insert_book(book_id, title, author)

        print("\nInitial tree state:")
        print(self.print_tree(self.tree.root))

        # Delete books in different positions and verify properties
        delete_order = [4, 2, 6, 1, 7, 3, 5]  # Test different deletion scenarios
        for book_id in delete_order:
            print(f"\nDeleting book {book_id}")
            self.tree.delete_book(book_id)
            
            print(f"Tree state after deleting book {book_id}:")
            print(self.print_tree(self.tree.root))
            
            result, message = self.verify_rb_properties()
            self.assertTrue(result, f"RB tree properties violated after deleting book {book_id}:\n{message}")
            
            # Verify the node is actually deleted
            self.assertIsNone(self.tree.find_node(book_id), f"Book {book_id} still exists after deletion")

    def test_reservation_heap_operations(self):
        """Test reservation heap functionality"""
        # Insert a test book
        node = self.tree.insert_book(1, "Test Book", "Test Author")
        
        # Test initial borrow
        success, message = self.tree.borrow_book(101, 1, 1)
        self.assertTrue(success)
        self.assertEqual(node.borrowed_by, 101)
        
        # Test adding reservations to heap
        for i, (patron_id, priority) in enumerate([
            (102, 3),  # High priority
            (103, 2),  # Medium priority
            (104, 1),  # Low priority
            (105, 3),  # Another high priority
        ], 1):
            success, message = self.tree.borrow_book(patron_id, 1, priority)
            self.assertFalse(success, f"Borrow should fail for reservation {i}")
            self.assertIn("reservation", message.lower())
        
        # Return book and verify highest priority reservation gets it
        success, message = self.tree.return_book(101, 1)
        self.assertTrue(success)
        self.assertIn("102", message, "Highest priority (patron 102) should get the book")
        
        # Verify heap properties after operations
        next_reservation = node.reservation_heap.delete()
        self.assertIsNotNone(next_reservation)
        self.assertEqual(next_reservation.patron_id, 105, 
                        "Next reservation should be patron 105 (high priority)")

    def test_heap_size_limit(self):
        """Test that reservation heap respects size limit"""
        node = self.tree.insert_book(1, "Test Book", "Test Author")
        
        # Borrow the book first
        success, _ = self.tree.borrow_book(101, 1, 1)
        self.assertTrue(success)
        
        # Try to add more reservations than the heap size
        for i in range(1, HEAP_SIZE + 2):
            success, message = self.tree.borrow_book(200 + i, 1, 1)
            if i <= HEAP_SIZE:
                self.assertFalse(success)
                self.assertIn("reservation", message.lower())
            else:
                self.assertFalse(success)
                self.assertIn("full", message.lower())

    def test_find_closest_book(self):
        """Test finding closest book by ID"""
        books = [
            (10, "Book 10", "Author 10"),
            (20, "Book 20", "Author 20"),
            (30, "Book 30", "Author 30"),
            (40, "Book 40", "Author 40"),
            (50, "Book 50", "Author 50")
        ]
        
        for book_id, title, author in books:
            self.tree.insert_book(book_id, title, author)
        
        # Test exact matches
        for book_id, _, _ in books:
            closest = self.tree.find_closest_book(book_id)
            self.assertEqual(closest.book_id, book_id)
        
        # Test values between nodes
        test_cases = [
            (15, 10),  # Closer to 10 than 20
            (25, 20),  # Closer to 20 than 30
            (35, 30),  # Closer to 30 than 40
            (45, 40),  # Closer to 40 than 50
        ]
        
        for target, expected in test_cases:
            closest = self.tree.find_closest_book(target)
            self.assertEqual(
                closest.book_id, 
                expected, 
                f"For target {target}, expected closest to be {expected} but got {closest.book_id}"
            )
        
        # Test values outside the range
        self.assertEqual(self.tree.find_closest_book(5).book_id, 10)  # Below minimum
        self.assertEqual(self.tree.find_closest_book(55).book_id, 50)  # Above maximum

    def test_tree_integrity_after_operations(self):
        """Test that tree maintains its integrity after mixed operations"""
        operations = [
            # (operation_type, book_id, title, author, patron_id, priority)
            ("insert", 10, "Book 10", "Author 10", None, None),
            ("insert", 5, "Book 5", "Author 5", None, None),
            ("insert", 15, "Book 15", "Author 15", None, None),
            ("borrow", 10, None, None, 101, 1),
            ("insert", 3, "Book 3", "Author 3", None, None),
            ("borrow", 5, None, None, 102, 2),
            ("return", 10, None, None, 101, None),
            ("delete", 15, None, None, None, None),
            ("insert", 12, "Book 12", "Author 12", None, None),
            ("borrow", 12, None, None, 103, 3),
        ]
        
        for op, book_id, title, author, patron_id, priority in operations:
            print(f"\nPerforming {op} operation on book {book_id}")
            
            if op == "insert":
                self.tree.insert_book(book_id, title, author)
            elif op == "borrow":
                self.tree.borrow_book(patron_id, book_id, priority)
            elif op == "return":
                self.tree.return_book(patron_id, book_id)
            elif op == "delete":
                self.tree.delete_book(book_id)
            
            print("Current tree state:")
            print(self.print_tree(self.tree.root))
            
            # Verify RB properties after each operation
            result, message = self.verify_rb_properties()
            self.assertTrue(
                result, 
                f"RB tree properties violated after {op} operation on book {book_id}:\n{message}"
            )
            
            # Verify BST property
            self.assertTrue(
                self.verify_bst_property(self.tree.root),
                f"BST property violated after {op} operation on book {book_id}"
            )

    def verify_bst_property(self, node):
        """Helper method to verify BST property"""
        if node == self.tree.nil:
            return True
            
        if node.left != self.tree.nil:
            if node.left.book_id >= node.book_id:
                return False
            if not self.verify_bst_property(node.left):
                return False
                
        if node.right != self.tree.nil:
            if node.right.book_id <= node.book_id:
                return False
            if not self.verify_bst_property(node.right):
                return False
                
        return True

    def test_concurrent_operations(self):
        """Test tree stability with multiple interleaved operations"""
        # Setup initial tree
        initial_books = [(i, f"Book {i}", f"Author {i}") for i in range(1, 6)]
        for book_id, title, author in initial_books:
            self.tree.insert_book(book_id, title, author)
        
        # Perform mixed operations
        operations = [
            # Borrow some books
            (lambda: self.tree.borrow_book(101, 1, 2)),
            (lambda: self.tree.borrow_book(102, 3, 1)),
            # Make reservations
            (lambda: self.tree.borrow_book(103, 1, 3)),
            (lambda: self.tree.borrow_book(104, 3, 2)),
            # Return books
            (lambda: self.tree.return_book(101, 1)),
            # Delete books with reservations
            (lambda: self.tree.delete_book(3)),
            # Insert more books
            (lambda: self.tree.insert_book(6, "Book 6", "Author 6")),
            # Borrow new books
            (lambda: self.tree.borrow_book(105, 6, 1)),
        ]
        
        for i, operation in enumerate(operations, 1):
            print(f"\nPerforming operation {i}")
            operation()
            
            print("Tree state:")
            print(self.print_tree(self.tree.root))
            
            # Verify tree properties
            result, message = self.verify_rb_properties()
            self.assertTrue(result, f"RB properties violated after operation {i}:\n{message}")
            
            self.assertTrue(
                self.verify_bst_property(self.tree.root),
                f"BST property violated after operation {i}"
            )

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test empty tree operations
        self.assertIsNone(self.tree.find_node(1))
        self.assertIsNone(self.tree.find_closest_book(1))
        self.assertEqual(self.tree.delete_book(1), [])
        
        # Test single node operations
        node = self.tree.insert_book(1, "Single Book", "Single Author")
        self.assertEqual(node.parent, self.tree.nil)
        
        # Test duplicate book_id (should be handled by Django's unique constraint)
        success, message = self.tree.borrow_book(101, 999, 1)
        self.assertFalse(success)
        self.assertIn("not found", message.lower())
        
        # Test invalid returns
        success, message = self.tree.return_book(102, 1)  # Wrong patron
        self.assertFalse(success)
        self.assertIn("not borrowed", message.lower())
        
        # Test reservation heap limits
        node = self.tree.insert_book(2, "Test Book", "Test Author")
        self.tree.borrow_book(101, 2, 1)  # First borrow
        
        # Fill reservation heap
        for i in range(HEAP_SIZE):
            self.tree.borrow_book(200 + i, 2, 1)
            
        # Try to exceed heap size
        success, message = self.tree.borrow_book(300, 2, 1)
        self.assertFalse(success)
        self.assertIn("full", message.lower())

    def test_color_flip_counting(self):
        """Test that color flips are being counted correctly"""
        initial_count = self.tree.get_color_flip_count()
        
        # Insert nodes that will require color flips
        test_cases = [
            (1, "Book 1", "Author 1"),
            (2, "Book 2", "Author 2"),
            (3, "Book 3", "Author 3"),
            (4, "Book 4", "Author 4"),
            (5, "Book 5", "Author 5")
        ]
        
        prev_count = initial_count
        for book_id, title, author in test_cases:
            self.tree.insert_book(book_id, title, author)
            current_count = self.tree.get_color_flip_count()
            
            # Count should never decrease
            self.assertGreaterEqual(
                current_count, 
                prev_count, 
                f"Color flip count decreased after inserting book {book_id}"
            )
            prev_count = current_count
        
        final_count = self.tree.get_color_flip_count()
        self.assertGreater(
            final_count, 
            initial_count, 
            "No color flips recorded during insertions"
        )
        
        print(f"Total color flips during test: {final_count - initial_count}")