import os
import json
import requests

from base64 import b64encode, b64decode
from collections import OrderedDict
from Crypto.PublicKey import RSA
from Crypto.Util import number
from datetime import datetime
from jwt import JWT, jwk_from_dict
from OpenSSL import crypto
from suds.client import Client
from xml.dom import minidom


class SystemUserToken:
    """
    Class used to exchange a system user token for a system user Ticket.
    A system user Ticket is one of the accepted credential types when calling
    SuperOffice web services.
    Attributes
    ----------
    app_token : str
        the application secret, or token.
    private_key_file : str
        the private certificate key filename.
    environment : str
        the subdomain used to determine the deployment target, i.e. sod, stage
        or online.
    Methods
    -------
    get_system_user_ticket(sys_token, context_id)
        uses the system user token to get the system user ticket credential
        for spefified tenant (context_id).
    """

    def get_long_int(self, nodelist):
        """converts contents of element as long int"""
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        string = ''.join(rc)
        return number.bytes_to_long(b64decode(string))

    #
    # gets the PEM cert from from Private RSA Key XML file.
    #

    def get_rsa_as_pem_content(self, file_name):
        '''returns a PEM from from Private RSA Key XML file.'''
        with open(file_name, 'rb') as pkFile:
            xmlPrivateKey = pkFile.read()
        rsaKeyValue = minidom.parseString(xmlPrivateKey)
        modulus = self.get_long_int(rsaKeyValue.getElementsByTagName(
            'Modulus')[0].childNodes)
        exponent = self.get_long_int(rsaKeyValue.getElementsByTagName(
            'Exponent')[0].childNodes)
        d = self.get_long_int(
            rsaKeyValue.getElementsByTagName('D')[0].childNodes)
        p = self.get_long_int(
            rsaKeyValue.getElementsByTagName('P')[0].childNodes)
        q = self.get_long_int(
            rsaKeyValue.getElementsByTagName('Q')[0].childNodes)
        qInv = self.get_long_int(rsaKeyValue.getElementsByTagName(
            'InverseQ')[0].childNodes)
        privateKey = RSA.construct((modulus, exponent, d, p, q, qInv), False)
        pemKey = privateKey.exportKey()
        return pemKey.decode('utf-8')

    def get_pem_content(self, file_name):
        '''returns contents from private RSA XML file.'''
        with open(file_name, 'rb') as pkFile:
            rsaFileContent = pkFile.read()
            return rsaFileContent.decode('utf-8')

    def get_private_key(self, file_name):
        if str(file_name).endswith('.xml'):
            return self.get_rsa_as_pem_content(file_name)
        elif str(file_name).endswith('.pem'):
            return self.get_pem_content(file_name)

    def __init__(self, app_token, private_key_file, environment='online'):
        self.application_token = app_token
        self.private_key = self.get_private_key(private_key_file)
        print(self.private_key)
        self.environment = environment

        self.login_endpoint = 'login/Services/PartnerSystemUserService.svc'
        self.wsdl_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'PartnerSystemUserService.wsdl')

    def get_system_user_ticket(self, sys_token, context_id):
        """
        returns Ticket credential string.
        Attributes
        ----------
        sys_token : str
        the tenant-specific system user token.
        context_id : str
        the customer identifier, i.e. Cust12345.
        """

        time_utc = datetime.utcnow()
        time_formatted = datetime.strftime(time_utc, "%Y%m%d%H%M")
        system_token = sys_token + '.' + time_formatted

        key = crypto.load_privatekey(crypto.FILETYPE_PEM, self.private_key)
        signature = crypto.sign(key, system_token, 'sha256')
        signed_system_token = system_token + "." + \
            b64encode(signature).decode('UTF-8')

        headers = OrderedDict([
            ('ApplicationToken', self.application_token),
            ('ContextIdentifier', context_id)
        ])

        client = Client('file:%s' % self.wsdl_path)
        client.set_options(soapheaders=headers)
        client.set_options(
            location='https://{env}.superoffice.com/{endpoint}'.format(
                env=self.environment, endpoint=self.login_endpoint))

        token_type = client.factory.create('TokenType')['Jwt']

        response = client.service.Authenticate(signed_system_token, token_type)

        if response.IsSuccessful == True:
            jwt_token = response.Token
            print('Reponse: ' + str(response))
            jwt = JWT()
            jwksResponse = requests.get(
                'https://{env}.superoffice.com/login/.well-known/jwks'.format(
                    env=self.environment))
            jwks = json.loads(jwksResponse.text)
            verifying_key = jwk_from_dict(jwks['keys'][0])
            message_received = jwt.decode(jwt_token, verifying_key)

            return str(message_received['http://schemes.superoffice.net/identity/ticket'])

        return 'Failed!'