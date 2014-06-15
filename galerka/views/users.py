import asyncio
import json

import wtforms
from wtforms import validators
from werkzeug.wrappers import Response

from galerka.view import GalerkaView
from galerka.views.index import TitlePage
from galerka.util import asyncached
from galerka import forms


class RegistrationForm(forms.Form):
    username = wtforms.StringField(
        'Přezdívka',
        [
            validators.Length(min=2, max=30,
                              message='Přezdívka musí mít 2 až 20 znaků'),
        ],
    )
    password = wtforms.PasswordField(
        'Heslo',
        [
            validators.Length(min=5,
                              message='Heslo by mělo mít alespoň 5 znaků'),
            validators.DataRequired(message='Heslo je povinné'),
            validators.EqualTo('password2',
                               message='Heslo a kontrola se musí shodovat'),
        ],
    )
    password2 = wtforms.PasswordField('Heslo znovu')


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
        if self.request.environ['REQUEST_METHOD'].upper() == 'POST':
            assert self.form
        else:
            self.form = form = RegistrationForm(prefix='newuser:')
        return (yield from self.render_template('user_new.mako'))

    @property
    def POST(self):
        self.form = form = RegistrationForm(self.request.form,
                                            prefix='newuser:')
        self.form_valid = form.validate()
        if self.form_valid:
            return self.handle_post()
        else:
            def ret():
                rendered = yield from self.rendered_page
                return Response(rendered, mimetype='text/html')
            return ret()

    @asyncio.coroutine
    def do_post(self):
        print(self.form_valid, self.form.data)
        # TODO
        ret = yield from self.request.execute_sql('SELECT 1')
        assert ret == (1, ), ret
        return '201 Created', json.dumps({'created': 'ok'}), self.url
