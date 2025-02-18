from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Book, Reservation
from .managers import gator_library

@receiver(post_save, sender=Book)
def update_tree_and_db(sender, instance, created, **kwargs):
    """Synchronize RB tree and database after book changes"""
    if created:
        print(f"DEBUG: Post-save signal for new book {instance.book_id}")
        # First insert into RB tree
        node = gator_library.rb_tree.insert_book(
            instance.book_id,
            instance.title,
            instance.author,
            instance.availability_status
        )
        
        print(f"DEBUG: Tree insertion complete. Updating DB")
        # Update database with pointers
        Book.objects.filter(pk=instance.book_id).update(
            parent_id=node.parent.book_id if node.parent != gator_library.rb_tree.nil else None,
            left_id=node.left.book_id if node.left != gator_library.rb_tree.nil else None,
            right_id=node.right.book_id if node.right != gator_library.rb_tree.nil else None
        )
        print(f"DEBUG: Database update complete for book {instance.book_id}")
        
        # Also update sibling and parent pointers in database
        if node.parent != gator_library.rb_tree.nil:
            Book.objects.filter(pk=node.parent.book_id).update(
                left_id=node.parent.left.book_id if node.parent.left != gator_library.rb_tree.nil else None,
                right_id=node.parent.right.book_id if node.parent.right != gator_library.rb_tree.nil else None
            )
            print(f"DEBUG: Updated parent {node.parent.book_id} pointers in database")
    else:
        print(f"DEBUG: Post-save signal for existing book {instance.book_id}")
        # For updates, sync the tree node with database
        node = gator_library.rb_tree.find_node(instance.book_id)
        if node:
            node.title = instance.title
            node.author = instance.author
            node.availability_status = instance.availability_status
            if instance.borrowed_by:
                node.borrowed_by = instance.borrowed_by.id
                
            # Update pointers in database
            Book.objects.filter(pk=instance.book_id).update(
                parent_id=node.parent.book_id if node.parent != gator_library.rb_tree.nil else None,
                left_id=node.left.book_id if node.left != gator_library.rb_tree.nil else None,
                right_id=node.right.book_id if node.right != gator_library.rb_tree.nil else None
            )

@receiver(post_delete, sender=Book)
def handle_book_deletion(sender, instance, **kwargs):
    """Handle book deletion"""
    print(f"DEBUG: Deleting book {instance.book_id}")
    gator_library.rb_tree.delete_book(instance.book_id)
    
@receiver(post_save, sender=Reservation)
def handle_reservation(sender, instance, created, **kwargs):
    """Handle reservation changes"""
    if created and instance.is_active:
        node = gator_library.rb_tree.find_node(instance.book.book_id)
        if node:
            success = node.reservation_heap.insert(
                instance.patron.id,
                instance.priority
            )
            if not success:
                instance.is_active = False
                instance.save()