import os
import dateutil.parser

from flask import request, redirect, render_template, url_for, session, current_app, flash

from work_uk import app, oauth, redis_client, forms

from decorators import registry_oauth_required

registry = oauth.remote_app(
    'registry',
    consumer_key=app.config['REGISTRY_CONSUMER_KEY'],
    consumer_secret=app.config['REGISTRY_CONSUMER_SECRET'],
    request_token_params={'scope': 'visa:add visa:view person:view'},
    base_url=app.config['REGISTRY_BASE_URL'],
    request_token_url=None,
    access_token_method='POST',
    access_token_url='%s/oauth/token' % app.config['REGISTRY_BASE_URL'],
    authorize_url='%s/oauth/authorize' % app.config['REGISTRY_BASE_URL']
)

@app.template_filter('visa_number')
def visa_number_filter(value):
    return value.split('/')[-1]

@app.template_filter('format_date')
def format_date_filter(value):
    date = dateutil.parser.parse(str(value))
    return date.strftime('%d %B %Y')


#auth helper
@registry.tokengetter
def get_registry_oauth_token():
    return session.get('registry_token')

#views
@app.route("/")
def index():
    return redirect("%s/work-visa" % app.config['WWW_BASE_URL'])

@app.route("/prove-status")
@registry_oauth_required
def prove_status():
    if not session.get('registry_token', False):
        return redirect(url_for('verify'))

    visas = registry.get('/visas').data
    if visas:
        visa = visas[0]
        code = _create_code(visa)
    else:
        visa = None
        code = None
    return render_template('prove_status.html', visa=visa, code=code)

@app.route("/prove-status/view/<visa_number>", methods=['GET', 'POST'])
@registry_oauth_required
def show_status_view(visa_number):
    if not session.get('registry_token', False):
        return redirect(url_for('verify'))

    form = forms.CheckCode(request.form)

    if form.validate_on_submit():
        visa = registry.get('/visas/'+visa_number).data
        if _check_code(form.code.data, visa):
            person = registry.get(visa['person_uri']).data
            return render_template('show_status_view.html', visa=visa, person=person)
        else:
            flash('Invalid code')
            return render_template('check_code.html', form=form)
    else:
        return render_template('check_code.html', form=form)

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
        resume_url = session.get('resume_url')
        session.pop('resume_url', None)
        return redirect(resume_url)
    else:
        return redirect(url_for('index'))


def _create_code(visa):
    import string, random, pickle
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.sample(chars, 5))
    visa_number = visa_number_filter(visa['uri'])
    stored_codes = redis_client.get(visa_number)
    if stored_codes:
        code_list = pickle.loads(stored_codes)
        code_list.append(code)
    else:
        code_list = [code]
    redis_client.set(visa_number, pickle.dumps(code_list))

    return code

def _check_code(code, visa):
    import pickle
    visa_number = visa_number_filter(visa['uri'])
    stored_codes = redis_client.get(visa_number)
    if stored_codes:
        code_list = pickle.loads(stored_codes)
        return code in code_list
    else:
        return False



