import json
import os
from pathlib import Path

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3

# Find the project config reliably whether Ryu is launched from the project root
# or the controller folder.
ROOT = Path(__file__).resolve().parent.parent
CONFIG_CANDIDATES = [
    ROOT / "config" / "project_config.json",
    ROOT / "project_config.json",
    ROOT / "config.json",
]
CONFIG_PATH = next((p for p in CONFIG_CANDIDATES if p.exists()), None)
if CONFIG_PATH is None:
    raise FileNotFoundError(
        "Cannot find project config. Expected config/project_config.json, "
        "project_config.json, or config.json under the project root."
    )

with CONFIG_PATH.open() as file:
    config = json.load(file)

RECEIVER_IP = config["server"]["host"]
SERVER_PORT = int(config["server"]["port"])
RECEIVER_SWITCH_PORT = int(config.get("switch", {}).get("receiver_port", 4))

BASELINE = os.environ.get("MODE", "priority").lower() == "baseline"

# Sender destination port -> queue ID. Part 2's SDN client sends to these
# classification ports; the controller rewrites the destination to SERVER_PORT.
CLASS_QUEUES = {5001: 1, 5002: 2, 5003: 3}


class PriorityController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Table-miss: allow ordinary traffic (ARP, ICMP, etc.) through OVS.
        self.add_flow(
            datapath, 0, parser.OFPMatch(),
            [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        )

        for udp_port, priority_queue in CLASS_QUEUES.items():
            queue_id = 1 if BASELINE else priority_queue
            match = parser.OFPMatch(
                eth_type=0x0800,
                ip_proto=17,
                ipv4_dst=RECEIVER_IP,
                udp_dst=udp_port,
            )
            actions = [
                parser.OFPActionSetQueue(queue_id),
                parser.OFPActionSetField(udp_dst=SERVER_PORT),
                parser.OFPActionOutput(RECEIVER_SWITCH_PORT),
            ]
            self.add_flow(datapath, 10, match, actions)

        self.logger.info(
            "Switch %s connected; mode=%s; receiver=%s:%s; output port=%s",
            datapath.id, "baseline" if BASELINE else "priority",
            RECEIVER_IP, SERVER_PORT, RECEIVER_SWITCH_PORT
        )

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        instructions = [
            parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)
        ]
        datapath.send_msg(
            parser.OFPFlowMod(
                datapath=datapath,
                priority=priority,
                match=match,
                instructions=instructions,
            )
        )
