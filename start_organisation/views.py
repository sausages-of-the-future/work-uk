import os
import jinja2
import json
import dateutil.parser
from flask import Flask, request, redirect, render_template, url_for, session, flash, abort
import requests
from flask_oauthlib.client import OAuth
import start_organisation.forms as forms
from start_organisation.order import Order
from start_organisation import app, oauth
from decorators import registry_oauth_required

service = {
  "name": "Start organisation",
  "minister": "Minister for business",
  "registers": ["Licences", "Organisations"],
  "slug": "start-organisation",
  "service_base_url_config": "ORGANISATIONS_BASE_URL",
  "policies": [],
  "legislation": [],
  "guides": [
    {"title": "Guide for Directors", "slug": "directors"},
    {"title": "Guide for Trustees", "slug": "trustees"},
    {"title": "Types of organisation", "slug": "types"}
  ]
}


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
    return redirect("%s/organisations" % app.config['WWW_BASE_URL'])
    return redirect(url_for('index'))

@app.route("/start")
def start():
    session.clear()
    if not session.get('registry_token', False):
        session['resume_url'] = 'choose_type'
        return redirect(url_for('verify'))
    else:
        return redirect(url_for('start_type'))

@app.route("/choose-type", methods=['GET', 'POST'])
@registry_oauth_required
def choose_type():

    # create order
    order = Order()
    order_data = session.get('order', None)
    if order_data:
        order = Order.from_dict(order_data)

    # create form and add options
    form = forms.StartOrganisationTypeForm(request.form)
    form.organisation_type.value = order.organisation_type

    if request.method == 'POST':
        order.organisation_type = form.organisation_type.data
        session['order'] = order.to_dict()
        return redirect(url_for('start_details'))

    return render_template('start-type.html', form=form)

@app.route("/start/details", methods=['GET', 'POST'])
@registry_oauth_required
def start_details():

    order = None
    order_data = session.get('order', None)
    if order_data:
        order = Order.from_dict(order_data)
    else:
        return redirect(url_for('start_type'))

    form = forms.StartOrganisationDetailsForm(request.form)

    if request.method == 'POST':
        data = {
            'organisation_type': order.organisation_type,
            'name': form.name.data,
            'activities': form.activities.data
        }

        response = registry.post('/organisations', data=data, format='json')
        if response.status == 201:
            flash('Organsiation created', 'success')
            session.pop('order', None)
            return redirect(url_for('index'))
        else:
            flash('Something went wrong', 'error')

    return render_template('start-details.html', form=form)

@app.route("/manage")
def manage():
    #for now, just redirect to the last one that was created
    uri = "%s/organisations" % app.config['REGISTRY_BASE_URL']
    response = requests.get(uri)
    if response.status_code == 200:
        organisations = response.json()
        organisation_uri = organisations[len(organisations) -1]['uri']
        organisation_id = organisation_uri.split("/")[len(organisation_uri.split("/")) - 1]
        return redirect(url_for('manage_organisation', organisation_id=organisation_id))
    else:
        abort(404)

@app.route("/manage/<organisation_id>")
def manage_organisation(organisation_id):
    uri = "%s/organisations/%s" % (app.config['REGISTRY_BASE_URL'], organisation_id)
    response = requests.get(uri)
    if response.status_code == 200:
        organisation = response.json()
    else:
        abort(404)

    return render_template("manage.html", organisation=organisation, service=service)

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


