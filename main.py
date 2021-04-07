from superofficesdk.SystemUserToken import SystemUserToken

# create instance of SystemUserToken
#   application_token: application secret
#   private_key_file:  file with .xml (RSAXML) or .pem file extension
#   environment:       'sod' | 'stage' | 'online'

systemuser = SystemUserToken('f6051dc60004abe621be860da7ca37de', 'superoffice.pem', 'online')

# get the system user ticket
#   system_user_token:  claim received by admin successful interactive login
#   context_identifier: customer id, i.e. Cust12345
#

ticket = systemuser.get_system_user_ticket('VFSSOClient-qM8IzmEUb2', 'Cust27125')

print('System user ticket: ' + ticket)