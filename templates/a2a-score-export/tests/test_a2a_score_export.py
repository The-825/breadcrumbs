import copy, hashlib, importlib.util, json
from pathlib import Path
import unittest

path = Path(__file__).parents[1] / "a2a_score_export.py"
spec = importlib.util.spec_from_file_location("exporter", path)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

def fixture():
    card = {"name":"Example Agent","description":"Example","supportedInterfaces":[{"url":"https://agent.example/a2a","protocolBinding":"JSONRPC","protocolVersion":"1.0"}],"version":"1.0.0","capabilities":{},"defaultInputModes":["text/plain"],"defaultOutputModes":["application/json"],"skills":[]}
    assessment = {"status":"published","target":{"name":"Example Agent"},"human_reviewed":True,"publication_approval":"approval-1","assessed_at":"2026-08-21T00:00:00Z"}
    digest = hashlib.sha256(json.dumps(assessment, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result = {"assessment_digest":digest,"target":"Example Agent","status":"published","evaluator_version":"0.1.0","evidence_coverage":0.75,"readiness_band":"governed"}
    return card, assessment, result

def run(card=None, assessment=None, result=None):
    f = fixture()
    return module.attach_score(card or f[0], assessment or f[1], result or f[2], "https://evidence.example/score.json", "2026-09-21T00:00:00Z", "2026-08-21T00:00:00Z")

class Tests(unittest.TestCase):
    def test_deterministic_non_required_extension(self): self.assertEqual(run(), run()); self.assertFalse(run()["capabilities"]["extensions"][0]["required"])
    def test_input_unchanged(self):
        card, assessment, result = fixture(); before = copy.deepcopy(card); run(card, assessment, result); self.assertEqual(before, card)
    def test_draft_refused(self):
        card, assessment, result = fixture(); assessment["status"]="draft"; self.assertRaises(module.ExportError, run, card, assessment, result)
    def test_target_mismatch_refused(self):
        card, assessment, result = fixture(); assessment["target"]["name"]="Other"; self.assertRaises(module.ExportError, run, card, assessment, result)
    def test_tamper_refused(self):
        card, assessment, result = fixture(); assessment["assessed_at"]="2026-08-22T00:00:00Z"; self.assertRaises(module.ExportError, run, card, assessment, result)
    def test_expiry_refused(self):
        c,a,r=fixture(); self.assertRaises(module.ExportError, module.attach_score, c,a,r,"https://evidence.example/x","2026-08-20T00:00:00Z","2026-08-21T00:00:00Z")
    def test_signed_refused(self):
        c,a,r=fixture(); c["signatures"]=[{}]; self.assertRaises(module.ExportError, run,c,a,r)
    def test_unknown_field_refused(self):
        c,a,r=fixture(); c["internalSkills"]=[{"secret":"sentinel"}]; self.assertRaises(module.ExportError, run,c,a,r)
    def test_private_endpoint_refused(self):
        c,a,r=fixture(); c["supportedInterfaces"][0]["url"]="https://127.0.0.1/a2a"; self.assertRaises(module.ExportError, run,c,a,r)
    def test_existing_extension_replaced(self):
        c,a,r=fixture(); c["capabilities"]["extensions"]=[{"uri":module.EXTENSION_URI}]; self.assertEqual(1,len(run(c,a,r)["capabilities"]["extensions"]))

if __name__ == "__main__": unittest.main()
