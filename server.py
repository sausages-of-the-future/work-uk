import os
import sys

port = int(os.environ.get('PORT'))

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
    os.environ['DEBUG'] = 'true'
    from start_organisation import app
    app.run(host='0.0.0.0', port=port)
