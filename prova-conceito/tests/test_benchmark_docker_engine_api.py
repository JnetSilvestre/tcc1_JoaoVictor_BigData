"""E11-I05: testes de parser, identidade e GET somente leitura; SEM Docker real."""
import json
import unittest

from benchmark.docker_engine_api import (
    assess, named_pipe_from_context, parse_http_response, parse_stats,
    identities, API_RE, DOCKER_ID_RE
)


class EngineProbeUnitTests(unittest.TestCase):
    def test_windows_pipe_whitelist(self):
        self.assertEqual(named_pipe_from_context("npipe:////./pipe/dockerDesktopLinuxEngine"),
                         "\\\\.\\pipe\\dockerDesktopLinuxEngine")
        self.assertEqual(named_pipe_from_context("npipe:////./pipe/docker_engine"),
                         "\\\\.\\pipe\\docker_engine")
        for value in ("tcp://localhost:2375", "ssh://example", "npipe:////./pipe/bad",
                      r"\\.\pipe\docker_engine"):
            with self.assertRaises(ValueError):
                named_pipe_from_context(value)
        self.assertTrue(API_RE.fullmatch("1.56"))
        self.assertTrue(DOCKER_ID_RE.fullmatch("a" * 64))
        self.assertFalse(DOCKER_ID_RE.fullmatch("../remove"))

    def test_plain_and_chunked_http(self):
        obj = {"read":"2026-11-16T02:00:00Z","cpu_stats":{"cpu_usage":{"total_usage":500}}}
        data = json.dumps(obj, separators=(",", ":")).encode()
        plain = (b"HTTP/1.1 200 OK\r\nContent-Length: " +
                 str(len(data)).encode() + b"\r\n\r\n" + data)
        chunked = (b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n"
                   + f"{len(data):x}\r\n".encode() + data + b"\r\n0\r\n\r\n")
        self.assertEqual(parse_http_response(plain), obj)
        self.assertEqual(parse_http_response(chunked), obj)
        with self.assertRaises(RuntimeError):
            parse_http_response(b"HTTP/1.1 404 Not Found\r\nContent-Length: 2\r\n\r\n{}")
        with self.assertRaises(ValueError):
            parse_http_response(plain[:-2])

    def test_stats_are_cumulative_and_memory_not_workingset(self):
        raw = {
            "read": "2026-11-16T02:00:00.000000Z",
            "cpu_stats": {"cpu_usage":{"total_usage":1005000000},
                          "throttling_data":{"throttled_periods":7,"throttled_time":4000}},
            "memory_stats":{"usage":11000000,"limit":268435456,
                            "stats":{"inactive_file":1000000}},
            "networks":{"eth0":{"rx_bytes":100,"tx_bytes":200}}
        }
        item = parse_stats(raw,"attribute-source","example","a"*64,0.2,"2026-11-16T02:00:02Z")
        self.assertEqual(item["cpu_total_ns"],1005000000)
        self.assertEqual(item["memory_usage_bytes"],11000000)
        self.assertEqual(item["memory_cli_adjusted_bytes"],10000000)
        self.assertEqual(item["cpu_throttled_periods"],7)
        self.assertEqual(item["network_rx_bytes"],100)
        self.assertNotIn("workingSetBytes",item)

    def test_missing_and_regressed_cpu_block_quality(self):
        base = {"role":"attribute-source", "cpu_total_ns":100,
                "memory_usage_bytes":6000}
        self.assertFalse(assess([base, {**base,"cpu_total_ns":50}],
                                ["attribute-source"])["fields_available_and_monotonic"])
        self.assertTrue(assess([base, {**base,"cpu_total_ns":110}],
                               ["attribute-source"])["fields_available_and_monotonic"])
        self.assertFalse(assess([base],["attribute-source"])["measurement_approved"])

    def test_name_only_e11_pilot(self):
        network,names=identities("p20261115-225314")
        self.assertEqual(network,"tcc2-pon-e11-c2-p20261115-225314")
        self.assertEqual(len(names),4)
        self.assertNotIn("tcc2-c2-attribute-source",names.values())


if __name__ == "__main__":
    unittest.main()
