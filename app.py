from flask import Flask, jsonify, render_template, request, session
from fire_flask import FireFlask
from mediagetter import web_search, news_search, getMedia

app = Flask(__name__)

# static pages
@app.route('/')
@app.route('/landing')
def index():
    return render_template('landing.html')


@app.route('/concept')
def concept():
    return render_template('concept.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/message')
def message():
    fire = FireFlask()
    fire.get_all_messages('messages')
    return render_template('message.html', messages=fire.payload)


@app.route('/put_message', methods=['POST'])
def put_message():

    message = request.form['message']
    media = request.form['media']

    fire = FireFlask()
    fire.login('testy@tester.com', 'XCNS900iNck')

    if message and media:
        fire._dataModel(message)
        fire.add_message('messages', fire.model, media)

        fire.get_recent('messages')
        name = fire.payload[0].get('text')

    elif message:
        fire._dataModel(message)
        fire.add_message('messages', fire.model)

        fire.get_recent('messages')
        #name = fire.payload[0].get('text')
        name = fire.payload[0]
    else:
        pass

    return jsonify({'name' : name})



@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/process', methods=['POST'])
def process():
    email = request.form['email']
    name = request.form['name']

    if name and email:
        newName = name[::-1]

        fire = FireFlask()
        fire.login('testy@tester.com', 'XCNS900iNck')

        fire._dataModel(newName)
        fire.add_message('messages', fire.model)
        fire.get_recent('messages')

        name = fire.payload[0].get('text')

        return jsonify({'name' : name})

    return jsonify({'error' : 'Missing data!'})

if __name__ == "__main__":
    app.run(debug=True)

