from recon.core.module import BaseModule

from censys.ipv4 import CensysIPv4
from censys.base import CensysException

class Module(BaseModule):
    meta = {
        'name': 'Censys hosts by hostname',
        'author': 'J Nazario',
        'description': 'Finds all IPs for a given hostname. Updates the "hosts" and "ports" tables.',
        'query': 'SELECT DISTINCT host FROM hosts WHERE host IS NOT NULL',
        'required_keys': ['censysio_id', 'censysio_secret'],
    }

    def module_run(self, hosts):
        api_id = self.get_key('censysio_id')
        api_secret = self.get_key('censysio_secret')
        c = CensysIPv4(api_id, api_secret)
        IPV4_FIELDS = [ 'ip', 'protocols', 'location.country', 
                        'location.latitude', 'location.longitude']        
        for host in hosts:
            self.heading(host, level=0)
            try:
                payload = [ x for x in c.search('a:{0}'.format(host), IPV4_FIELDS) ]
            except CensysException:
                continue
            for result in payload:
                self.add_hosts(host=host, 
                               ip_address=result['ip'], 
                               country=result.get('location.country', ''),
                               latitude=result.get('location.latitude', ''), 
                               longitude=result.get('location.longitude', ''))
                for protocol in result['protocols']:
                    port, service = protocol.split('/')
                    self.add_ports(ip_address=result['ip'], port=port, protocol=service)
