from django import forms
from .models import Book, Reservation

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['priority']
        widgets = {
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }

class BookSearchForm(forms.Form):
    target_id = forms.IntegerField(
        label='Find Closest Book ID',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )