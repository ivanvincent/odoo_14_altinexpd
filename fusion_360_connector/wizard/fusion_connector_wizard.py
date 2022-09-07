from email.policy import default
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import requests
import json

SCOPE = "user-profile:read user:read user:write viewables:read data:read data:write data:create data:search bucket:create bucket:read bucket:update bucket:delete code:all account:read account:write"

class FusionConnectorWizard(models.TransientModel):
    _name = 'fusion.connector.wizard'

    client_id = fields.Char(string='Client Id')
    client_secret = fields.Char(string='Client Secret')
    scope = fields.Char(string='Scope', default=SCOPE)
    result = fields.Char(string='Result')
    is_connected = fields.Boolean(string='Is Connect ?', default=False)

    def connect_to_fusion(self):
        print("connect_to_fusion")
        url = "https://developer.api.autodesk.com/authentication/v1/authenticate"
        payload='client_id='+ self.client_id +'&client_secret='+ self.client_secret+'&grant_type=client_credentials&scope=user-profile%3Aread%20user%3Aread%20user%3Awrite%20viewables%3Aread%20data%3Aread%20data%3Awrite%20data%3Acreate%20data%3Asearch%20bucket%3Acreate%20bucket%3Aread%20bucket%3Aupdate%20bucket%3Adelete%20code%3Aall%20account%3Aread%20account%3Awrite'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        res = json.loads(response.text)
        self.result = response.text
        if response:
            self.is_connected = True
            set_param = self.env['ir.config_parameter'].set_param
            set_param('fusion_client_id', self.client_id)
            set_param('fusion_secret_id', self.client_secret)
            set_param('fusion_scope', self.scope)
            set_param('fusion_access_token', res.get('access_token', False))
            set_param('fusion_token_type', res.get('token_type', False))            
            set_param('fusion_token_expire', res.get('expires_in', False))            


        action = self.env.ref('fusion_360_connector.fusion_connector_wizard_action').read()[0]
        action['res_id'] = self.id
        return action

    @api.model
    def default_get(self, fields):
        result = super(FusionConnectorWizard, self).default_get(fields)
        get_param = self.env['ir.config_parameter'].sudo().get_param
        result.update({
            'client_id': get_param("fusion_client_id", False),
            'client_secret': get_param("fusion_secret_id", False),
            # 'scope': get_param("fusion_scope", False),
            'scope': SCOPE,
            })
        return result

    def action_get_project(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        client_id = get_param("fusion_client_id", False)
        client_server = get_param("fusion_secret_id", False)
        token_type = get_param("fusion_token_type", False)
        access_token =  get_param('fusion_access_token', False)

        url = "https://developer.api.autodesk.com/fusiondata/2022-04/graphql"

        payload="{\"query\":\"query {\\n  hubs {\\n    results {\\n      name\\n    }\\n  }\\n}\",\"variables\":{}}"
        headers = {
        'Accept': 'application/json',
        'Authorization': '%s %s' % (token_type, access_token),
        'Content-Type': 'application/json',
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)