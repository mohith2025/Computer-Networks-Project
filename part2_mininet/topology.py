
#!/usr/bin/env python3

from mininet.topo import Topo


class LogAggregationTopo(Topo):
    def build(self):
        # Three log-generating clients
        h1 = self.addHost('H1', ip='10.0.0.1/24')
        h2 = self.addHost('H2', ip='10.0.0.2/24')
        h3 = self.addHost('H3', ip='10.0.0.3/24')

        # Log receiver
        hr = self.addHost('HR', ip='10.0.0.4/24')

        # OpenFlow switch
        s1 = self.addSwitch('s1', protocols='OpenFlow13')

        # Connect every host to the switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(hr, s1)


topos = {
    'logtopo': lambda: LogAggregationTopo()
}
