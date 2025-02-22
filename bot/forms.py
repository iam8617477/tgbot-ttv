from django import forms


class EmailForm(forms.Form):
    email = forms.EmailField(
        required=True,
        error_messages={'invalid': 'Please enter a valid email address.'}
    )
