
# Udep2Mono: Monotonicity Marking from Universal Dependency Trees

This framework provides an easy and accurate method to annotate monotonicity information (polarity arrows) on natural English sentences based on Universal Dependency parse trees.  

The following publications are integrated in this framework:
- [Monotonicity Marking from Universal Dependency Trees](https://arxiv.org/abs/1908.10084) (IWCS 2021)

## Installation
The recoomanded environment include **Python 3.6** or higher , **[Stanza v1.2.0](https://github.com/stanfordnlp/stanza)** or higher, and **[ImageMagick v7.0.11](https://imagemagick.org/script/download.php). The code does **not** work with Python 2.7.

**Clone the repository**
```
git clone https://github.com/eric11eca/Udep2Mono.git
```

**Install from sources**
```
pip install -r requirements.txt
python -m pip install --upgrade setuptools
python setup.py install
```

## Getting Started

First download a pretrained model from [Google Drive](https://drive.google.com/drive/folders/1XHCHA2inUs-1CfCXobFL0Feaw-eEsO5Y?usp=sharing). Replace the Stanza defalut depparse model with this pretrained version. The Stanza model path is: 
````
C:\Users\$your_user_name$\stanza_resources\en\
````
Then either open Udep2Mono.ipynb (recommanded) or run
````
python main.py
````

## Pre-Trained UD Parser Models

We provide two [UD Parser Models](https://drive.google.com/drive/folders/1XHCHA2inUs-1CfCXobFL0Feaw-eEsO5Y?usp=sharing) for English. Some models are general purpose models, while others produce embeddings for specific use cases. Pre-trained models can be loaded by just passing the model name: `SentenceTransformer('model_name')`.

## Training
For training new UD parser models, see [Stanza's training dcumentation](https://stanfordnlp.github.io/stanza/training.html#setting-environment-variables) for an introduction how to train your own UD parser. 

## Citing & Authors
If you find this repository helpful, feel free to cite our publication [Monotonicity Marking from Universal Dependency Trees](https://arxiv.org/abs/1908.10084):
```bibtex 
@article{DBLP:journals/corr/abs-2104-08659,
  author    = {Zeming Chen and
               Qiyue Gao},
  title     = {Monotonicity Marking from Universal Dependency Trees},
  journal   = {CoRR},
  volume    = {abs/2104.08659},
  year      = {2021},
  url       = {https://arxiv.org/abs/2104.08659},
  archivePrefix = {arXiv},
  eprint    = {2104.08659},
  timestamp = {Mon, 26 Apr 2021 17:25:10 +0200},
  biburl    = {https://dblp.org/rec/journals/corr/abs-2104-08659.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```
Contact person: [Zeming Chen], [chenz16@rose-hulman.edu](mailto:chenz16@rose-hulman.edu)
Don't hesitate to send us an e-mail or report an issue, if something is broken or if you have further questions.

> This repository contains experimental software and is published for the sole purpose of giving additional background details on the respective publication.
