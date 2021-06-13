from flask import Flask, render_template, request, jsonify
from polarization import PolarizationPipeline

app = Flask(__name__)

pipeline = PolarizationPipeline()


@app.route('/')
def index():
    return render_template('udep2mono.html')


@app.route('/annotate', methods=['POST'])
def annotate():
    content = request.json
    sentences = content['sentences']
    trees = []
    for sentence in sentences:
        annotation = pipeline.single_polarization(sentence)
        tree = pipeline.postprocess(annotation["polarized_tree"])
        trees.append(tree)

    return jsonify({"annotations": trees})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
