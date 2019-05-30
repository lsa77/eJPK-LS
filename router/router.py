import falcon
import xml.etree
import os
import requests
from wsgiref import simple_server

xml.etree.ElementTree.register_namespace('asx','http://www.sap.com/abapxml')


class XMLHandler(falcon.media.BaseHandler):

    def deserialize(self, stream, content_type, content_length):
        media = stream.read().decode('utf-8')
        print(media)
        return media

    def serialize(self, media, content_type):
        #result = media.encode('utf-8')
        result = media
        print(media)
        return result


xml_handler = XMLHandler()

extra_handlers = {
    'application/xml': xml_handler,
}


class NegotiationMiddleware(object):
    def process_request(self, req, resp):
        resp.content_type = req.accept


class RouterPost:
    def __init__(self):
        self.root_element: xml.etree.ElementTree = xml.etree.ElementTree.Element('DUMMY')
        self.xml_no_license_element: bytes = b''
        self.xml_data: bytes = b''

    def on_post(self, req, resp):
        print(req.media)

        self.root_element = xml.etree.ElementTree.fromstring(req.media.encode())

        resp.media = 'No XML data provided. Failed to parse anyway.'

        if self.root_element is not None:
            self.remove_license_tag()
            self.xml_no_license_element = xml.etree.ElementTree.tostring(self.root_element, encoding="utf8", method='xml')
            self.xml_no_license_element = RouterPost.correct_tags_xml(self.xml_no_license_element)

            # get_signature using xml_data
            url = self.get_signer_url()

            url+= '/signature-pkcs7'
            headers = {'Content-Type': 'application/xml'}

            print(url)
            response = requests.post(url=url, headers=headers, data=self.xml_no_license_element )
            print(response.content)

            signature = response.content

            signature = signature.replace(b'-----BEGIN PKCS7-----\n', b'')
            signature = signature.replace(b'\n-----END PKCS7-----\n', b'')

            while signature.find(b'\n') != -1:
                signature = signature.replace(b'\n', b'')

            self.add_license(signature)

            self.xml_data = xml.etree.ElementTree.tostring(self.root_element, encoding="utf8", method='xml')
            self.xml_data = RouterPost.correct_tags_xml(self.xml_data)

            resp.media = self.xml_data
            print(str(resp.media))

    def get_signer_url(self):
        return os.environ['SIGNER_URL']


    def remove_license_tag(self):
        for data in self.root_element.iter('DATA'):
            for lic in data.iter('LICENSE'):
                if lic.tag == 'LICENSE':
                    data.remove(lic)

    @staticmethod
    def correct_tags_xml(input_string: bytes):
        corrected = input_string.replace(b"'utf8'", b'"utf-8"')
        corrected = corrected.replace(b"'1.0'", b'"1.0"')

        corrected = corrected.replace(b'<LNOTE />', b'<LNOTE/>')
        corrected = corrected.replace(b'<CMPNM />', b'<CMPNM/>')
        corrected = corrected.replace(b'<REFNR />', b'<REFNR/>')

        return corrected

    def add_license(self, signature):
        license_element = xml.etree.ElementTree.Element('LICENSE')
        license_element.text = str(signature, 'UTF-8')

        for data in self.root_element.iter('DATA'):
            data.insert(1, license_element)


if __name__ == '__main__':

    api = falcon.API(media_type=falcon.MEDIA_XML, middleware=NegotiationMiddleware())

    api.add_route('/sign', RouterPost())

    api.req_options.media_handlers.update(extra_handlers)
    api.resp_options.media_handlers.update(extra_handlers)

    httpd = simple_server.make_server('0.0.0.0', 5000, api)
    httpd.serve_forever()