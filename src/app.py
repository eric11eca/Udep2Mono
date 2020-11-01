from flask import Flask, render_template, request, jsonify
from flask_restful import reqparse, abort, Api, Resource

from polarization import run_polarize_pipeline

app = Flask(__name__)
api = Api(app)


@app.route('/')
def index():
    return render_template('udep2mono.html')


@app.route('/annotate', methods=['POST'])
def annotate():
    content = request.json
    sentences = content['sentences']
    annotations, exceptioned, incorrect = run_polarize_pipeline(
        sentences, verbose=2)
    return jsonify({"annotations": annotations})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
