from work_uk import app
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

app.run(host="0.0.0.0", port=int(os.environ['PORT']), debug=True)
