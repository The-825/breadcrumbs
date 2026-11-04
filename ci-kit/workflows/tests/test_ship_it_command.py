"""Execute the installed whole-comment parser without GitHub mutations."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]

class ShipItCommandTests(unittest.TestCase):
    def test_verified_actor_and_whole_comment_parser(self):
        paths = [ROOT / '.github/workflows/greenlight-command.yml']
        template = ROOT / 'ci-kit/workflows/greenlight-command.yml'
        if template.exists():
            paths.append(template)
        git_bash = Path('C:/Program Files/Git/bin/bash.exe')
        bash = str(git_bash) if os.name == 'nt' and git_bash.exists() else shutil.which('bash')
        self.assertIsNotNone(bash, 'The release parser requires bash')
        for path in paths:
            text = path.read_text(encoding='utf-8')
            self.assertIn('github.event.issue.pull_request', text)
            self.assertIn('github.event.comment.user.login)', text)
            self.assertIn('APPROVAL_LABEL: ship-it', text)
            match = re.search(r'        run: \|\n(.*?)\n      - name: Acknowledge', text, re.S)
            self.assertIsNotNone(match)
            script = '\n'.join(line[10:] for line in match.group(1).splitlines())
            for body, expected in [('ship it',True),(' ship it\r\n',True),('greenlight',True),('gl',True),('do not ship it',False),('ship it later',False),('ship it\nCodex',False),('ship it; touch injected',False),('$(touch injected)',False)]:
                with self.subTest(path=path, body=body), tempfile.TemporaryDirectory() as tmp:
                    env = dict(os.environ, BODY=body, GITHUB_OUTPUT='output.txt')
                    run = subprocess.run([bash,'-c',script],cwd=tmp,env=env,capture_output=True,text=True)
                    self.assertEqual(0,run.returncode,run.stderr)
                    self.assertIn('match='+str(expected).lower(),(Path(tmp)/'output.txt').read_text())
                    self.assertFalse((Path(tmp)/'injected').exists())

if __name__ == '__main__':
    unittest.main()
