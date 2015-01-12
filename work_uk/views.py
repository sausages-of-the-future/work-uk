import os
import jinja2
import json
import dateutil.parser
from flask import Flask, request, redirect, render_template, url_for, session, flash, abort
import requests
from flask_oauthlib.client import OAuth
import work_uk.forms as forms
from work_uk import app, oauth
from decorators import registry_oauth_required

registry = oauth.remote_app(
    'registry',
    consumer_key=app.config['REGISTRY_CONSUMER_KEY'],
    consumer_secret=app.config['REGISTRY_CONSUMER_SECRET'],
    request_token_params={'scope': 'organisation:add'},
    base_url=app.config['REGISTRY_BASE_URL'],
    request_token_url=None,
    access_token_method='POST',
    access_token_url='%s/oauth/token' % app.config['REGISTRY_BASE_URL'],
    authorize_url='%s/oauth/authorize' % app.config['REGISTRY_BASE_URL']
)

#auth helper
@registry.tokengetter
def get_registry_oauth_token():
    return session.get('registry_token')

#views
@app.route("/")
def index():
    return redirect("%s/work-uk" % app.config['WWW_BASE_URL'])

@app.route("/prove-status")
def prove_status():
    if not session.get('registry_token', False):
        session['resume_url'] = 'prove_status'
        return redirect(url_for('verify'))
    return render_template('prove_status.html')

@app.route("/prove-status/<slug>")
def show_status(slug):
    return render_template('show_status.html', slug=slug)

@app.route("/prove-status/<slug>/view")
def show_status_view(slug):
    return render_template('show_status_view.html')


@app.route("/sponsorship")
def sponsorship():
    return render_template('sponsorship.html')

@app.route('/verify')
def verify():
    _scheme = 'https'
    if os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', False) == 'true':
        _scheme = 'http'
    return registry.authorize(callback=url_for('verified', _scheme=_scheme, _external=True))

@app.route('/verified')
def verified():

    resp = registry.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
        request.args['error_reason'],
        request.args['error_description']
        )

    session['registry_token'] = (resp['access_token'], '')
    if session.get('resume_url'):
        return redirect(url_for(session.get('resume_url')))
    else:
        return redirect(url_for('index'))


