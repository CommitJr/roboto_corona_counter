import threading
from flask import Flask, jsonify
from src import consts
from src.cv_recogniser import run_cv_recogniser

app = Flask(__name__)


@app.route('/get', methods=['GET'])
def get_counter():
    return jsonify({
        'total': consts.total,
        'out': consts.ppl_out,
        'in': consts.ppl_in
    })


th = threading.Thread(target=run_cv_recogniser)
th.start()
app.run(debug=True, use_reloader=False)
