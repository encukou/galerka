import wtforms
from wtforms import validators

from galerka.view import GalerkaView
from galerka.views.index import TitlePage
from galerka.util import asyncached
from galerka import forms


class RegistrationForm(forms.Form):
    username = wtforms.StringField(
        'Přezdívka',
        [
            validators.Length(min=2, max=30,
                              message='Jméno musí mít 2 až 30 znaků'),
            validators.DataRequired(message='Jméno je povinné'),
        ],
    )
    password = wtforms.PasswordField(
        'Heslo',
        [
            validators.Length(min=8,
                              message='Heslo by mělo mít minimálně 5 znaků'),
            validators.DataRequired(message='Heslo je povinné'),
        ],
    )
    password2 = wtforms.PasswordField(
        'Heslo znovu',
        [validators.DataRequired(message='Kontrola hesla je povinná')],
    )


@TitlePage.child('users')
class UsersView(GalerkaView):
    @asyncached
    def title(self):
        return 'Uživatelé'

    @asyncached
    def rendered_contents(self):
        return '...'  # TODO


@UsersView.child('new')
class NewUserView(UsersView):
    @asyncached
    def title(self):
        return 'Nový účet'

    @asyncached
    def rendered_contents(self):
        self.form = form = RegistrationForm(prefix='newuser:')
        print(list(form))
        return (yield from self.render_template('user_new.mako'))
