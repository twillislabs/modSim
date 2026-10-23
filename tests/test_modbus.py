"""Tests for static register write-once behaviour (no TCP listener is started)"""
from modSim.modbus import Server

HR = 3


def make_server():
    return Server(0, register_sizes={"co": 10, "di": 10, "hr": 10, "ir": 10},
                  slaves=[{"slave_id": 0}])


def static_hr(value, address=2):
    return {
        "server_id": 0,
        "slave_id": 0,
        "register_type": "hr",
        "address": address,
        "simulate": True,
        "simulation_mode": "static",
        "simulation_config": {"value": value},
    }


class TestStaticRegisters:
    """A static rule is written when new or changed; client writes then persist"""

    def test_client_write_persists(self):
        server = make_server()
        registers = [static_hr(42)]
        server.simulate(registers)

        # A Modbus client (e.g. Ignition) writes a new value
        server.write_registers(0, HR, 2, [123])
        server.simulate(registers)

        assert server.read_registers(0, HR, 2) == [123]

    def test_changed_rule_is_rewritten(self):
        server = make_server()
        server.simulate([static_hr(42)])
        server.write_registers(0, HR, 2, [123])

        server.simulate([static_hr(50)])

        assert server.read_registers(0, HR, 2) == [50]
