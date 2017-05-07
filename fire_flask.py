import itertools
import json
import pyrebase
import requests
import datetime


class FireFlask:


    def __init__(self):

        #Note these config details will need to be modified and reflected in your Firebase application setup details.
        self.fire_config = {
            "apiKey": "GET YOUR OWN KEY",
            "authDomain": "AUTHENTICATION KEY",
            "databaseURL": "LOCATION OF YOUR DB",
            "storageBucket": "STORAGE LOCATION",
            "messagingSenderId": "MESSENGER ID"
        }

        self.firebase = pyrebase.initialize_app(self.fire_config)

        self.auth = self.firebase.auth()


    def login(self, email, password):

        self.user = self.auth.sign_in_with_email_and_password(email, password)

        if self.user['registered'] == True:
            self.message = {'result': 'logged'}
            return self.message, self.user
        else:
            self.message = {'result': 'please register an account.'}
            return self.message



    def add_user(self, email, password, user_data):

        self.user = self.auth.create_user_with_email_and_password(email, password)
        self.data = user_data
        self.data['user_id'] = self.user['localId']

        db = self.firebase.database()

        if self.user['registered'] == True:
            self.message = {'result': 'registered'}
            return self.message
        else:
            db.child('users').push(self.data)
            self.message = {'result': 'registered'}
            return self.message


    def add_media(self, user_id, pub_date, media_data):
        self.store = self.firebase.storage()
        loc = 'images/' + user_id + pub_date
        self.store.child(loc).put(media_data, self.user['idToken'])
        self.media_url = self.store.child(loc).get_url(self.user['idToken'])
        return self.media_url


    def add_node(self, node_data): #data needs to be in a dictionary format
        db = self.firebase.database()
        node_data['user_id'] = self.user['localId']
        node = dict(attributes=node_data)
        self.n_data = db.child('graph').child('node').push(node, self.user['idToken'])
        return self.n_data


    def add_edge(self, sourceId, targetId):
        db = self.firebase.database()
        edges = dict(edge_sourceId=sourceId, edge_targetId=targetId)
        self.edge_data = db.child('graph').child('edge').push(edges, self.user['idToken'])
        return self.edge_data


    def _dataModel(self, text):
        date_time = str(datetime.datetime.now())

        date = list(date_time.split(' '))
        time = date[1].split('.')

        self.model = {'pub_text': text,
                      'pub_id': self.user['localId'],
                      'pub_date': date,
                      'pub_time': time,
                      'pub_email': self.user['email'],
                      'location': dict(lat=86.56700, lon=120.0129)
                      }

        return self.model



    def add_message(self, endpoint, model_data, media=None):
        db = self.firebase.database()

        user_id = self.model['pub_id']
        pub_date = self.model['pub_date']

        if media:
            url = self.add_media(user_id, pub_date, media)
            self.model['media_url'] = url

            payload = dict(message=self.model)

            db.child(endpoint).push(payload, self.user['idToken'])

            self.msg_response = {'message': "message added"}
            return self.msg_response
        else:
            self.model['media_url'] = ''
            payload = dict(message=self.model)
            db.child(endpoint).push(payload, self.user['idToken'])
            self.msg_response = {'message': "message added"}
            return self.msg_response



    def get_recent(self, endpoint):
        db = self.firebase.database()

        data = db.child(endpoint).order_by_key().limit_to_last(1).get()

        self.payload = []

        for item in data.each():

            message = {
                'text': item.val().get('message').get('pub_text'),
                'url': item.val().get('message').get('media_url'),
                'date': item.val().get('message').get('pub_date'),
                'user': item.val().get('message').get('pub_id'),
                'time': item.val().get('message').get('pub_time'),
                'lat': item.val().get('message').get('location').get('lat'),
                'lon:': item.val().get('message').get('location').get('lon')
            }

            # self.payload[str(count)] = message
            # count = count + 1
            self.payload.append(message)

        return self.payload



    def get_all_messages(self, endpoint):
        db = self.firebase.database()
        data = db.child(endpoint).get()

        #self.payload = {}
        self.payload = []

        #count = 0
        for item in data.each():

            message = {
                'text': item.val().get('message').get('pub_text'),
                'url': item.val().get('message').get('media_url'),
                'date': item.val().get('message').get('pub_date'),
                'time': item.val().get('message').get('pub_time'),
                'lat': item.val().get('message').get('location').get('lat'),
                'lon:': item.val().get('message').get('location').get('lon')
            }

            #self.payload[str(count)] = message
            #count = count + 1
            #putting the in a format for prepending a list of items at the top
            self.payload.append(message)
            self.payload = list(reversed(self.payload))
        return self.payload



    def get_user_messages(self, user_id, endpoint):
        db = self.firebase.database()

        check = db.child(endpoint).get()

        self.payload = {}

        count = 0
        for item in check.each():
            if item.val().get('message').get('pub_id') == user_id:
                self.payload[str(count)] = [item.val().get('message')]
                count = count+1

        return self.payload


    def stream_msg(self, message):
        self.event = message["event"]  # put
        self.path =  message["path"]  # /-K7yGTTEp7O549EzTYtI
        self.data = message["data"]  # {'title': 'Pyrebase', "body": "etc..."}
        #print(event, path, data)


    def emit_stream(self, endpoint):
        db = self.firebase.database()
        x = db.child(endpoint).stream(self.stream_msg)
        while x:
            print(x)




