from werkzeug.serving import run_simple

from galerka.app import application

run_simple('localhost', 4000, application)
