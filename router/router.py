from flask import Flask
import requests

app = Flask(__name__)

payload = '<?xml version="1.0" encoding="utf-8"?><asx:abap version="1.0" xmlns:asx="http://www.sap.com/abapxml"><asx:values><DATA><KBJPR>JPK</KBJPR><EXPDT>2020-04-28</EXPDT><SAPCK>P0203380088</SAPCK><SAPIN>0120034711</SAPIN><TAXID>PL7691967641</TAXID><CRDAT>2019-04-29</CRDAT><REFNR/><CMPNM>TERMOKOR KAEFER Sp. z o.o.</CMPNM><LNOTE/></DATA></asx:values></asx:abap>'


@app.route('/b64encode')
def hello_world():

    url = 'ejpk-backend-signer-service.default.svc.cluster.local:80/b64encode'
    headers = {'content-type': 'text/xml'}


    response = requests.post(url=url, headers=headers, data=payload   )

    print(response)

    return response.content


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')