from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book
from .forms import BookForm, ReservationForm
from .managers import gator_library

@login_required
def book_list(request):
    # Get books from database for display
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'borrow':
            # Use RB tree for borrowing logic
            success, message = gator_library.borrow_book(
                request.user.id,
                book_id,
                request.POST.get('priority', 1)
            )
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
                
        elif action == 'return':
            # Use RB tree for return logic
            success, message = gator_library.return_book(request.user.id, book_id)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
    
    return render(request, 'library/book_detail.html', {
        'book': book,
        'form': ReservationForm(),
    })

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            # Insert book using RB tree
            node = gator_library.insert_book(
                form.cleaned_data['title'],
                form.cleaned_data['author']
            )
            messages.success(request, f'Successfully added book')
            return redirect('book_detail', book_id=node.book_id)
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    if request.method == 'POST':
        # Delete using RB tree
        cancelled_reservations = gator_library.delete_book(book_id)
        if cancelled_reservations:
            messages.info(request, 
                f'Book deleted. Cancelled reservations for patrons: {", ".join(map(str, cancelled_reservations))}')
        else:
            messages.success(request, 'Book deleted successfully')
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})

@login_required
def find_closest_book(request):
    target_id = request.GET.get('target_id')
    if target_id:
        try:
            target_id = int(target_id)
            # Find closest book using RB tree
            closest_node = gator_library.find_closest_book(target_id)
            if closest_node:
                return redirect('book_detail', book_id=closest_node.book_id)
            messages.error(request, 'No books found in the library')
        except ValueError:
            messages.error(request, 'Please enter a valid book ID')
    return redirect('book_list')

@login_required
def color_flip_count(request):
    count = gator_library.get_color_flip_count()
    return render(request, 'library/color_flip_count.html', {'count': count})