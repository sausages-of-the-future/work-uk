import os
import jinja2
import forms
import json
import hashlib
from order import Order
import dateutil.parser
from flask import Flask, request, redirect, render_template, url_for, session, flash, abort
from flask.json import JSONEncoder
from flask_oauthlib.client import OAuth
from start_organisation import app, oauth
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
    return render_template('index.html')

@app.route("/start", methods=['GET', 'POST'])
@registry_oauth_required
def start_type():

    # create order
    order = Order()
    order_data = session.get('order', None)
    if order_data:
        order = Order.from_dict(order_data)

    # create form and add options
    form = forms.StartOrganisationForm(request.form)
    form.organisation_type.choices = []
    data = json.loads(open('organisation_types.json').read())
    for item in data:
        form.organisation_type.choices.append(("%s/%s" % (app.config['BASE_URL'], item['slug']), item['name']))
    form.organisation_type.value = order.type_uri

    if request.method == 'POST':
        order.type_uri = form.organisation_type.data
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

    if request.method == 'POST':
        data = {
            'type_uri': order.type_uri,
            'name': 'my company'
        }
        response = registry.post('/organisations', data=data, format='json')
        if response.status == 201:
            flash('Organsiation created', 'success')
            session.pop('order', None)
            return redirect(url_for('index'))
        else:
            flash('Something went wrong', 'error')


    return render_template('start-details.html')

@app.route("/types")
def types():
    return render_template('types.html')

@app.route("/types/public-limited-company")
def types_public_limited_company():
    return render_template('type.html', name="Public Limited Company", detail_template="_types-public-limited-company.html")

@app.route("/types/private-limited-company")
def types_private_limited_company():
    return render_template('type.html', name="Private company limited by guarantee", detail_template="_types-private-limited-company.html")

@app.route("/types/ordinary-business-partnership")
def types_ordinary_business_partnership():
    return render_template('type.html', name="Ordinary Business Partnership", detail_template='_types-ordinary-business-partnership.html')

@app.route("/types/limited-partnership")
def types_limited_partnership():
    return render_template("type.html", name="Limited Partnership", detail_template='_types-limited-partnership.html')

@app.route("/types/limited-liability-partnership")
def types_limited_liability_partnership():
    return render_template("type.html", name="Limited Liability Partnership", detail_template='_types-limited-liability-partnership.html')

@app.route("/types/unincorperated-association")
def types_unincorperated_association():
    return render_template("type.html", name="Unincorperated Association", detail_template='_types-unincorperated-association.html')

@app.route("/types/charity")
def types_charity():
    return render_template("type.html", name="Charity", detail_template='_types-charity.html')

@app.route("/types/charitable-incorperated-organisation")
def types_charitable_incorperated_organisation():
    return render_template("type.html", name="Charitable Incorperated Organisation", detail_template='_types-charitable-incorperated-organisation.html')

@app.route("/types/cooperative")
def types_cooperative():
    return render_template("type.html", name="Co-operative", detail_template='_types-cooperative.html')

@app.route("/types/industrial-and-provident-society")
def types_industrial_and_provident_society():
    return render_template("type.html", name="Industrial and Provident Society", detail_template='_types-industrial-and-provident-society.html')

@app.route("/types/community-interest-company")
def types_community_interest_company():
    return render_template("type.html", name="Community Interest Company", detail_template='_types-community-interest-company.html')

@app.route('/verify')
def verify():
    return registry.authorize(callback=url_for('verified', _external=True))

@app.route('/verified')
def verified():

    resp = registry.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
        request.args['error_reason'],
        request.args['error_description']
        )

    session['registry_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))

