from quart import Quart, render_template, redirect, url_for, jsonify, Response, request
from donapp.session import start_whatsapp, get_status_details, get_qr, get_result

app = Quart("donapp")

@app.route('/')
async def index():
    if 'sid' in request.args:
        sid = request.args.get('sid')
    else:
        sid = 'test'
    return await render_template("index.html", sid=sid)


@app.route('/start/')
async def start():
    sid = request.args.get('sid')
    id = start_whatsapp(n_chats=10)
    return redirect(url_for("extract", id=id, sid=sid))

@app.route('/extract/<id>')
async def extract(id):
    sid=request.args.get('sid')
    return await render_template("qr.html", **locals())

@app.route('/qr_status/<id>')
async def qr_status(id):
    sid = request.args.get('sid')
    return jsonify(get_status_details(id))

@app.route('/qr/<id>')
async def qr(id):
    sid = request.args.get('sid')
    qr = get_qr(id)
    return jsonify({"qr": qr})

@app.route('/prepare/<id>')
async def prepare_download(id):
    sid = request.args.get('sid')
    return await render_template("prepare.html", **locals())

@app.route('/scrape_status/<id>')
async def scrape_status(id):
    return jsonify(get_status_details(id))

@app.route('/download/<id>')
async def download(id):
    sid = request.args.get('sid')
    return await render_template("download.html", **locals())

@app.route('/downloadfile/<id>')
async def download_file(id):
    #TODO: Verify IP Address
    result = get_result(id)
    return Response(result, mimetype='application/json',
                    headers={'Content-Disposition':'attachment;filename=whatsapp.json'})

@app.route('/error/<id>')
async def error(id):
    sid = request.args.get('sid')
    status = get_status_details(id)
    return await render_template("error.html", sid=sid, **status)
