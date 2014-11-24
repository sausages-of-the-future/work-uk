import os
import sys

port = int(os.environ.get('PORT'))

if __name__ == '__main__':
    from start_organisation import app
    app.run(host='0.0.0.0', port=port)
