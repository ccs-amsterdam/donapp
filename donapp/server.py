from quart import Quart, render_template, redirect, url_for, jsonify, Response
from donapp.session import start_whatsapp, get_status_details, get_qr, get_result

app = Quart("donapp")

@app.route('/')
async def index():
    return await render_template("index.html")


@app.route('/start/')
async def start():
    id = start_whatsapp(n_chats=2)
    return redirect(url_for("extract", id=id))

@app.route('/extract/<id>')
async def extract(id):
    return await render_template("qr.html", **locals())

@app.route('/qr_status/<id>')
async def qr_status(id):
    return jsonify(get_status_details(id))

@app.route('/qr/<id>')
async def qr(id):
    qr = get_qr(id)
    return jsonify({"qr": qr})

@app.route('/prepare/<id>')
async def prepare_download(id):
    return await render_template("prepare.html", **locals())

@app.route('/scrape_status/<id>')
async def scrape_status(id):
    return jsonify(get_status_details(id))

@app.route('/download/<id>')
async def download(id):
    return await render_template("download.html", **locals())

@app.route('/downloadfile/<id>')
async def download_file(id):
    #TODO: Verify IP Address
    result = get_result(id)
    return Response(result, mimetype='application/json',
                    headers={'Content-Disposition':'attachment;filename=whatsapp.jsonl'})

@app.route('/error/<id>')
async def error(id):
    status = get_status_details(id)
    return await render_template("error.html", **status)
