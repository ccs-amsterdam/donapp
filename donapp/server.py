import logging

from flask import Flask, url_for, jsonify, Response,  render_template, redirect

from donapp.session import start_whatsapp, get_status_details, get_qr, get_result

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-7s] %(message)s')

app = Flask("donapp")
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/start/')
def start():
    id = start_whatsapp(n_chats=2)
    return redirect(url_for("extract", id=id))

@app.route('/extract/<id>')
def extract(id):
    return render_template("qr.html", **locals())

@app.route('/qr_status/<id>')
def qr_status(id):
    return jsonify(get_status_details(id))

@app.route('/qr/<id>')
def qr(id):
    qr = get_qr(id)
    return jsonify({"qr": qr})

@app.route('/prepare/<id>')
def prepare_download(id):
    return render_template("prepare.html", **locals())

@app.route('/scrape_status/<id>')
def scrape_status(id):
    return jsonify(get_status_details(id))

@app.route('/download/<id>')
def download(id):
    return render_template("download.html", **locals())

@app.route('/downloadfile/<id>')
def download_file(id):
    #TODO: Verify IP Address
    result = get_result(id)
    return Response(result, mimetype='application/json',
                    headers={'Content-Disposition':'attachment;filename=whatsapp.jsonl'})

@app.route('/error/<id>')
def error(id):
    status = get_status_details(id)
    return render_template("error.html", **status)
