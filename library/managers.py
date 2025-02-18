class GatorLibraryManager:
    def __init__(self):
        print("Initializing GatorLibraryManager")
        self.rb_tree = None
        self._initialize_tree()

    def _initialize_tree(self):
        print("Initializing RB tree")
        from .data_structures.rb_tree import GatorLibrary
        self.rb_tree = GatorLibrary()
        # Load existing books from database into RB tree
        from .models import Book
        books = Book.objects.all()
        print(f"Loading {books.count()} books from database into RB tree")
        for book in books:
            print(f"Inserting book {book.book_id}: {book.title}")
            self.rb_tree.insert_book(
                book.book_id,
                book.title,
                book.author,
                book.availability_status
            )

    def insert_book(self, title, author):
        """Insert a new book into the RB tree and database"""
        from .models import Book
        print(f"Creating new book: {title} by {author}")
        # First save to database to get book_id
        book = Book.objects.create(
            title=title,
            author=author,
            availability_status="Yes"
        )
        print(f"Book created in database with ID: {book.book_id}")
        # Then insert into RB tree
        node = self.rb_tree.insert_book(
            book.book_id,
            title,
            author,
            "Yes"
        )
        print(f"Book inserted into RB tree")
        return node

    def borrow_book(self, patron_id, book_id, priority=1):
        """Borrow a book using RB tree operations"""
        print(f"Attempting to borrow book {book_id} for patron {patron_id}")
        node = self.rb_tree.find_node(book_id)
        if not node:
            print(f"Book {book_id} not found in RB tree")
            return False, "Book not found"

        success, message = self.rb_tree.borrow_book(patron_id, book_id, priority)
        print(f"Borrow attempt result: {success}, {message}")
        if success:
            # Update database to match RB tree state
            from .models import Book
            book = Book.objects.get(book_id=book_id)
            book.availability_status = "No"
            book.borrowed_by_id = patron_id
            book.save()
            print(f"Database updated for book {book_id}")
        return success, message

    def return_book(self, patron_id, book_id):
        """Return a book using RB tree operations"""
        success, message = self.rb_tree.return_book(patron_id, book_id)
        if success:
            # Update database to match RB tree state
            from .models import Book
            book = Book.objects.get(book_id=book_id)
            if "allocated to patron" in message:
                next_patron_id = int(message.split()[-1])
                book.borrowed_by_id = next_patron_id
            else:
                book.availability_status = "Yes"
                book.borrowed_by = None
            book.save()
        return success, message

    def delete_book(self, book_id):
        """Delete a book using RB tree operations"""
        cancelled_reservations = self.rb_tree.delete_book(book_id)
        # Update database
        from .models import Book
        Book.objects.filter(book_id=book_id).delete()
        return cancelled_reservations

    def find_closest_book(self, target_id):
        """Find closest book using RB tree operations"""
        return self.rb_tree.find_closest_book(target_id)

    def get_color_flip_count(self):
        """Get the number of color flips in the RB tree"""
        return self.rb_tree.get_color_flip_count()

# Global instance of the library manager
gator_library = GatorLibraryManager()