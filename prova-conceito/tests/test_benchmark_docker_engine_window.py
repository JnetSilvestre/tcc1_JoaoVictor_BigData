"""E11-I06: testes sinteticos da janela Docker, sem Docker real ou POST."""
import unittest
from datetime import datetime, timedelta, timezone

from benchmark.docker_engine_window import EngineSampler, quality_window


class EngineWindowQualityTests(unittest.TestCase):
    def make_data(self, seconds=16):
        base = datetime(2026,11,16,3,0,0,tzinfo=timezone.utc)
        cid = "a"*64
        rows=[]
        for i in range(seconds):
            stamp=(base+timedelta(seconds=i)).isoformat()
            rows.append({
                "role":"attribute-source","container_id":cid,
                "cpu_total_ns":i*100_000_000,
                "memory_usage_bytes":1_000_000+i,
                "docker_read_utc":stamp,
                "retrieved_utc":(base+timedelta(seconds=i, milliseconds=150)).isoformat(),
            })
        summary={
            "batch_started_utc":(base+timedelta(seconds=2)).isoformat(),
            "batch_finished_utc":(base+timedelta(seconds=13)).isoformat(),
            "elapsed_ns":11_000_000_000,
        }
        return rows,{ "attribute-source":cid },summary

    def test_complete_window_is_temporally_adequate_but_not_approved(self):
        rows,ids,summary=self.make_data()
        result=quality_window(rows,ids,summary)
        self.assertTrue(result["cpu_counters_available"])
        self.assertTrue(result["cpu_window_adequate"])
        self.assertFalse(result["measurement_approved"])
        self.assertFalse(result["memory_comparable_to_kubelet"])
        self.assertAlmostEqual(result["roles"]["attribute-source"]["cpu_delta_bracketing_s"],1.1)

    def test_short_batch_rejected_even_with_valid_counter(self):
        rows,ids,summary=self.make_data()
        summary["batch_finished_utc"]=rows[3]["docker_read_utc"]
        summary["elapsed_ns"]=1_000_000_000
        result=quality_window(rows,ids,summary)
        self.assertTrue(result["cpu_counters_available"])
        self.assertFalse(result["cpu_window_adequate"])

    def test_counter_regression_and_identity_mismatch_rejected(self):
        rows,ids,summary=self.make_data()
        rows[5]["cpu_total_ns"]=0
        self.assertFalse(quality_window(rows,ids,summary)["cpu_counters_available"])
        rows,ids,summary=self.make_data()
        rows[7]["container_id"]="b"*64
        self.assertFalse(quality_window(rows,ids,summary)["cpu_window_adequate"])

    def test_stale_source_timestamp_rejected(self):
        rows,ids,summary=self.make_data()
        rows[8]["retrieved_utc"]=(datetime.fromisoformat(rows[8]["docker_read_utc"])
                                  +timedelta(seconds=11)).isoformat()
        result=quality_window(rows,ids,summary)
        self.assertFalse(result["roles"]["attribute-source"]["source_timestamp_fresh"])
        self.assertFalse(result["cpu_window_adequate"])

    def test_duplicated_timestamp_at_boundary_blocks_cpu(self):
        rows,ids,summary=self.make_data()
        rows[3]["docker_read_utc"]=rows[2]["docker_read_utc"]
        # Valor diferente, mesma hora na fronteira inicial.
        result=quality_window(rows,ids,summary)
        self.assertTrue(result["cpu_counters_available"])
        self.assertEqual(result["roles"]["attribute-source"]["ambiguous_source_timestamps"],1)
        self.assertFalse(result["cpu_window_adequate"])

    def test_utc_and_monotonic_disagreement_rejected(self):
        rows,ids,summary=self.make_data()
        summary["elapsed_ns"]=20_000_000_000
        result=quality_window(rows,ids,summary)
        self.assertFalse(result["clock_coherent"])
        self.assertFalse(result["cpu_window_adequate"])

    def test_sampler_uses_only_engine_interface(self):
        class FakeEngine:
            def check_local_engine(self):
                return {"api_version":"1.56","pipe":"dummy","endpoint":"npipe:////./pipe/docker_engine"}
            def assert_new_pilot_containers(self,names):
                return {role:"a"*64 for role in names}
            def engine_stat(self,pipe,api,cid,role,name):
                return {"role":role,"container_id":cid,"cpu_total_ns":1,
                        "memory_usage_bytes":1,"docker_read_utc":"2026-11-16T03:00:00Z",
                        "retrieved_utc":"2026-11-16T03:00:00Z"}
        names={role:role for role in ("attribute-source","logic-engine","rule-executor","client")}
        sampler=EngineSampler(names,period=1,engine_module=FakeEngine())
        sampler.preflight()
        sampler.prime()
        self.assertEqual(len(sampler.samples),4)
        self.assertEqual(len(sampler.rounds),1)
        self.assertEqual(sampler.context_record()["api_version"],"1.56")


if __name__=="__main__":
    unittest.main()
