
from flask import Flask, render_template, request, redirect
import os
import json
from werkzeug import secure_filename
import urllib.request
import pandas as pd


app = Flask(__name__)
UPLOAD_FOLDER = "/home/PracticeProjects/bpHw/webApps/static/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['csv'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload():
    return render_template("fileupload.html")


@app.route('/upload', methods=['POST'])
def uploader():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return redirect(request.url)
    files = request.files.getlist('files[]')
    csvlist = []
    for file in files:
        print('Files uploaded', files, file.filename)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            csvlist.append(UPLOAD_FOLDER+filename)
            file.save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(csvlist)

    order2data = pd.read_csv(csvlist[0])
    order1data = pd.read_csv(csvlist[1])
    resdataF = pd.concat([order1data, order2data], ignore_index=True)
    resdataF['Total Marketplace Charges'] = resdataF['Commission'] + \
        resdataF['Payment Gateway']+resdataF['PickPack Fee']
    resdataF['Profit/loss%'] = (resdataF['Sale Amount'] -
                                resdataF['Cost Price'] - resdataF['Total Marketplace Charges'])
    resdataF['Profit/loss%'] = round((resdataF['Profit/loss%']) / (
        resdataF['Cost Price'] + resdataF['Total Marketplace Charges'])*100, 2)
    display = resdataF[["OrderNum", "Profit/loss%",
                        'Transferred Amount', 'Total Marketplace Charges']]
    result = display.to_json(orient="records")
    parsed = json.loads(result)
    # print(parsed)
    return render_template("dispData.html", data=display.to_html(classes=["table-bordered", "table-striped", "table-hover"], index=False))


if __name__ == '__main__':
    app.run(debug=True)
