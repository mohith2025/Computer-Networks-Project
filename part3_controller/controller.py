import json
import os

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3

# Run ryu-manager from the project root because this path is relative.
with open("config/project_config.json") as file:
    config = json.load(file)

RECEIVER_IP = config["server"]["host"]      # HR = 10.0.0.4
RECEIVER_SWITCH_PORT = 4                    # s1 port facing HR (s1-eth4)
SERVER_PORT = config["server"]["port"]      # 9999

# MODE=baseline -> every class shares queue 1 (no priority, same 10 Mbps limit)
# MODE=priority (default) -> each class uses its own queue
BASELINE = os.environ.get("MODE", "priority") == "baseline"

# Classifier: UDP destination port used by the sender -> OVS queue ID
# 5001 = INFO, 5002 = WARNING/ERROR, 5003 = CRITICAL
CLASS_QUEUES = {
    5001: 1,
    5002: 2,
    5003: 3,
}


class PriorityController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Default rule: everything else (ARP, ping, replies) uses normal switching.
        self.add_flow(datapath, 0, parser.OFPMatch(),
                      [parser.OFPActionOutput(ofproto.OFPP_NORMAL)])

        # One rule per class: match the UDP port, pick the queue, then send to HR
        # using the port the server listens on.
        for udp_port, queue_id in CLASS_QUEUES.items():
            if BASELINE:
                queue_id = 1
            match = parser.OFPMatch(eth_type=0x0800, ip_proto=17,
                                    ipv4_dst=RECEIVER_IP, udp_dst=udp_port)
            actions = [
                parser.OFPActionSetQueue(queue_id),
                parser.OFPActionSetField(udp_dst=SERVER_PORT),
                parser.OFPActionOutput(RECEIVER_SWITCH_PORT),
            ]
            self.add_flow(datapath, 10, match, actions)

        mode = "baseline (no priority)" if BASELINE else "priority"
        self.logger.info("Switch %s connected, mode=%s, rules installed", datapath.id, mode)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        datapath.send_msg(parser.OFPFlowMod(datapath=datapath, priority=priority,
                                            match=match, instructions=instructions))
