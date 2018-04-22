from flask import Flask, request, jsonify, url_for
from flask_restful import reqparse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import auth
from werkzeug.contrib.atom import AtomFeed
from lib.PostCode import PostCode
from lib.ImportResponse import ImportResponse
from pymongo import MongoClient
from dicttoxml import dicttoxml


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'BOCSAR data'


@app.route('/authorization', methods=['post'])
def authorization():
    accounts = [
        ('admin', 'admin'),
        ('admin1', '1111'),
        ('guest01', '1'),
        ('guest02', '2'),
        ('guest03', '3'),
    ]
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str)
    parser.add_argument('password', type=str)
    args = parser.parse_args()
    username = args.get("username")
    password = args.get("password")
    s = Serializer(auth.key, expires_in=1800)
    token = s.dumps(username)
    if (username, password) in accounts:
        return jsonify(token=token.decode())
    else:
        return jsonify(errmsg='Wrong user name or password'), 400


@app.route('/nsw', methods=['post'])
@auth.admin_required
def fetch():
    parser = reqparse.RequestParser()
    parser.add_argument('lgaName', type=str)
    parser.add_argument('postcode', type=int)
    args = parser.parse_args()
    lga = args.get('lgaName')
    postcode = args.get('postcode')
    accept = request.accept_mimetypes.best_match(['application/json', 'application/atom+xml'])
    postcodeSearch = PostCode()
    response = ImportResponse()
    # if input is lga
    if lga is not None:
        codes = postcodeSearch.getCodesByLga(lga)
        if codes:
            responseId, responseContent, updateTime = response.get(lga)
            if responseId == response.USED_TO_UPDATED_BEFORE or responseId == response.UPDATE_SUCCESSFULLY:
                if accept == 'application/atom+xml':
                    feed = AtomFeed('Update result', id=url_for('fetch', _external=True))
                    feed.add(responseContent, '==PLACE_HOLDER==', content_type='application/xml',
                             id=url_for('view', lga=lga.replace(' ', '').lower(), _external=True),
                             updated=updateTime, author='BOCSAR',)
                    feedString = feed.to_string().\
                        replace('==PLACE_HOLDER==', dicttoxml({'postcode': codes}, root=False).decode())
                    if responseId == response.USED_TO_UPDATED_BEFORE:
                        return feedString
                    elif responseId == response.UPDATE_SUCCESSFULLY:
                        return feedString, 201
                else:
                    if responseId == response.USED_TO_UPDATED_BEFORE:
                        return jsonify({'postcode': codes})
                    elif responseId == response.UPDATE_SUCCESSFULLY:
                        return jsonify({'postcode': codes}), 201
            else:
                return jsonify(errmsg='LGA has no data'), 500
        else:
            return jsonify(errmsg='Invalid LGA'), 400
    # if input is post code
    elif postcode is not None:
        lgas = postcodeSearch.getLgasByCode(postcode)
        if lgas:
            feed = AtomFeed('Update result', id=url_for('fetch', _external=True))
            updateResults = []
            replace = []
            for someLga in lgas:
                responseId, responseContent, updateTime = response.get(someLga)
                if accept == 'application/atom+xml':
                    feed.add(responseContent, '==PLACE_HOLDER_' + someLga + '==', content_type='application/xml',
                             id=url_for('view', lga=someLga.replace(' ', '').lower(), _external=True),
                             updated=updateTime,
                             author='BOCSAR' if responseId != response.LGA_HAS_NO_DATA else 'Nobody')
                    replace.append(('==PLACE_HOLDER_' + someLga + '==', {'postcode': postcode}))
                else:
                    updateResults.append({'LGA': someLga, 'result': responseContent})
            if accept == 'application/atom+xml':
                feedString = feed.to_string()
                for holder, replacer in replace:
                    feedString = feedString.replace(holder, dicttoxml(replacer, root=False).decode())
                return feedString
            else:
                return jsonify(postcodes=postcode, update=updateResults)
        else:
            return jsonify(errmsg='Invalid Postcode'), 400
    # if nothing input
    else:
        return jsonify(errmsg='LGA name or post code required'), 400


@app.route('/nsw/<target>', methods=['delete'])
@auth.admin_required
def delete(target):
    return 'delete'


@app.route('/nsw', methods=['get'])
@auth.login_required
def collections():
    client = MongoClient('mongodb://as2:9321as2@ds249299.mlab.com:49299/nsw')
    for collection in client.nsw.collection_names():
        print(collection)
    return 'collections'


@app.route('/nsw/<lga>', methods=['get'])
@auth.login_required
def view(lga):
    return 'document'


if __name__ == '__main__':
    app.run()
