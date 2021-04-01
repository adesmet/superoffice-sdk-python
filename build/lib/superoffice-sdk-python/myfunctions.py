def get_system_ticket(system_user_token: str, contextId: str, client_secret: str, partner_private_key: str, superoffice_public_key: str) -> str:
    """
    Exchange a long-lived system user token for a short-lived system ticket, which can be used to call the SuperOffice REST API's. 
    :param system_user_token: the system user token provided as a claim in the callback (Redirect URL) when a tenant administrator successfully signs into SuperID.
    :param contextId: your online sandbox customer identifier
    :param client_secret: the client secret you have received upon app registration
    :param partner_private_key: the partner's private key, received upon application registration
    :param superoffice_public_key: the SuperOffice public key
    :return: the system ticket used to cnnect to the SuperOffice REST API's.
    """
    
    return 0