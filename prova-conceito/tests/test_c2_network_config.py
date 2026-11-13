"""Regressões da parametrização de transporte C1 -> C2, sem Docker."""

from io import BytesIO
from unittest import TestCase
from unittest.mock import Mock, patch

from c1.client import request
from c1.service import build_role, main


class NetworkConfigurationTests(TestCase):
    def test_client_uses_internal_dns_hostname(self):
        opener = Mock()
        opener.open.return_value = BytesIO(b'{"ready":true}')
        with patch("c1.client.build_opener", return_value=opener):
            result = request(8080, "/health/ready", host="logic-engine")
        self.assertEqual(result, {"ready": True})
        outgoing = opener.open.call_args.args[0]
        self.assertEqual(outgoing.full_url, "http://logic-engine:8080/health/ready")
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 5)

    def test_source_forwards_snapshot_to_named_service(self):
        with patch("c1.service.request", return_value={"ready": True}) as forward:
            state, _ = build_role(
                "attribute-source", 8080, lambda *args, **kwargs: None,
                downstream_host="logic-engine",
            )
            self.assertTrue(state.initialize("c2-check")["ready"])
        self.assertEqual(forward.call_args.args[1], "/init/snapshot")
        self.assertEqual(forward.call_args.kwargs["host"], "logic-engine")

    def test_cli_preserves_c1_default_and_accepts_c2_network(self):
        with patch("sys.argv", ["service", "rule-executor", "--port", "8080"]), \
                patch("c1.service.serve") as serve:
            main()
            serve.assert_called_once_with(
                "rule-executor", 8080, None,
                listen_host="127.0.0.1", downstream_host="127.0.0.1",
            )
        with patch("sys.argv", [
            "service", "attribute-source", "--port", "8080",
            "--downstream-port", "8080", "--listen-host", "0.0.0.0",
            "--downstream-host", "logic-engine",
        ]), patch("c1.service.serve") as serve:
            main()
            serve.assert_called_once_with(
                "attribute-source", 8080, 8080,
                listen_host="0.0.0.0", downstream_host="logic-engine",
            )
