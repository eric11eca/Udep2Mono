from flask import Flask, render_template, request, jsonify
from polarization import run_polarize_pipeline

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('udep2mono.html')


@app.route('/annotate', methods=['POST'])
def annotate():
    content = request.json
    sentences = content['sentences']
    annotations, _ = run_polarize_pipeline(
        sentences, verbose=2, parser="stanford")
    return jsonify({"annotations": annotations})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
