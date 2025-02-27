# Gator Library Management System

A library management system built with Django, implementing a Red-Black Tree data structure for efficient book management and a Min Heap for handling book reservations.

## Features

### Core Functionality
- **Red-Black Tree Implementation**: Efficient book storage and retrieval
- **Priority-based Reservation System**: Min Heap implementation for handling book reservations
- **Real-time Color Flip Tracking**: Monitor RB tree balancing operations
- **Closest Book Search**: Find books with IDs closest to a target value

### User Features
- User Authentication and Authorization
- Book Borrowing and Returns
- Priority-based Book Reservations
- Book Search and Management

### Administrative Features
- Book Addition and Deletion
- Reservation Management
- System Statistics Tracking

## Technical Stack

- **Backend**: Django 5.0
- **Database**: MySQL
- **Data Structures**: 
  - Custom Red-Black Tree implementation
  - Priority Queue using Min Heap

## Installation

1. Clone the repository
```bash
git clone https://github.com/AmithPremGit/gator-library.git
cd gator-library
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure MySQL Database
```bash
# Create a MySQL database named 'gator_library'
mysql -u root -p
CREATE DATABASE gator_library;
```

5. Update Database Settings
- Open `gator_library/settings.py`
- Update the database configuration with your MySQL credentials

6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Create Superuser
```bash
python manage.py createsuperuser
```

8. Run the Development Server
```bash
python manage.py runserver
```

## Usage

1. **User Registration and Login**
   - Access the system through the login page
   - New users can be created by admin

2. **Book Management**
   - Add new books through the interface
   - View book details and availability
   - Search for books using book ID

3. **Borrowing System**
   - Users can borrow available books
   - Place reservations with priority levels
   - Return books when finished

4. **Monitoring**
   - Track color flips in the Red-Black Tree
   - Monitor system performance
   - View reservation queues

## Data Structure Implementation

### Red-Black Tree
- Self-balancing binary search tree
- Guarantees O(log n) time complexity for operations
- Maintains balance through color properties

### Min Heap
- Priority queue implementation for reservations
- Efficient handling of priority-based requests
- Limited to 20 reservations per book

## Project Structure

```
gator_library/                  # Root Directory
├── manage.py
├── gator_library/             # Project Configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── library/                   # Main App Directory
    ├── migrations/
    ├── templates/
    │   └── library/          # Template Files
    │       ├── base.html
    │       ├── book_list.html
    │       ├── book_detail.html
    │       ├── book_form.html
    │       ├── book_confirm_delete.html
    │       ├── color_flip_count.html
    │       └── login.html
    ├── data_structures/      # Custom Data Structures
    │   ├── __init__.py
    │   ├── rb_tree.py       # Red-Black Tree Implementation
    │   └── min_heap.py      # Min Heap Implementation
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── managers.py
    ├── models.py
    ├── signals.py
    ├── urls.py
    └── views.py
```

## Testing

The project includes comprehensive tests for both data structures:

```bash
python manage.py test library.tests
```

Tests cover:
- Red-Black Tree operations
- Reservation system functionality
- Edge cases and boundary conditions
