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

registers = oauth.remote_app(
    'registers',
    consumer_key='c1aedf2d9fa74884930392850712c0a6',
    consumer_secret='00952aff578e476b93c7a10e9a1cbb05',
    request_token_params={'scope': 'person:view personal_licence:view personal_licence:add'},
    base_url='http://localhost:5000',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='http://localhost:5000/oauth/token',
    authorize_url='http://localhost:5000/oauth/authorize'
)

#auth helper
@registers.tokengetter
def get_registers_oauth_token():
    return session.get('registers_token')

#views
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/start", methods=['GET', 'POST'])
def start_type():

    if not session.get('registers_token', False):
        return redirect(url_for('verify'))

    return render_template('start-type.html')

@app.route("/types")
def types():
    return render_template('types.html')

@app.route("/types/limited-company")
def types_limited_company():
    return render_template('type.html', name="Limited Company", detail_template="_types-limited-company.html")

@app.route("/types/ordinary-business-partnership")
def types_ordinary_business_partnership():
    return render_template('type.html', name="Ordinary Business Partnership", detail_template='_types-ordinary-business-partnership.html')

@app.route("/types/limited-partnership")
def types_limited_partnership():
    return render_template("type.html", name="Limited Partnership", detail_template='_types-limited-partnership.html')

@app.route("/types/limited-liability-partnership")
def types_limited_liability_partnership():
    return render_template("type.html", name="Limited Liability Partnership", detail_template='_types-limited-liability-partnership.html')

@app.route("/types/types_unincorperated_association")
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
    return registers.authorize(callback=url_for('verified', _external=True))

@app.route('/verified')
def verified():

    resp = registers.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
        request.args['error_reason'],
        request.args['error_description']
        )

    session['registers_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))

