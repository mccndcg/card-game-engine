from flask import Flask, render_template, request, jsonify, make_response
import json
app = Flask(__name__)

@app.route('/')
def idx():
    return render_template('main.html')


@app.route("/get_states", methods=('GET','POST'))
def get_state():
    req = request.get_json()
    print(req)
    with open('states.json', encoding="utf8") as json_file:
        res = make_response(jsonify(json.load(json_file)))
        print(res)
        return res


if __name__ == '__main__':
    app.run()
