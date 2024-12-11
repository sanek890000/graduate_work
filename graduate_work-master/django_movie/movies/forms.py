from django import forms

from .models import Reviews, Rating, RatingStar


class ReviewForm(forms.ModelForm):
    # Форма отзывов
    class Meta:
        model = Reviews
        fields = ("name", "email", "text")


class RatingForm(forms.ModelForm):
    # Форма добавления рейтинга
    star = forms.ModelChoiceField(
        queryset=RatingStar.objects.all(), widget=forms.RadioSelect(), empty_label=None
    )

    class Meta:
        model = Rating
        fields = ("star",)


class ConnectionForm(forms.Form):
    # Форма обратной связи
    name = forms.CharField(max_length=255, label='Имя')
    email = forms.EmailField(label='Email')
    content = forms.CharField(label='Сообщение',
                              widget=forms.Textarea(attrs={'style': 'width:100%', 'rows': 10}))
