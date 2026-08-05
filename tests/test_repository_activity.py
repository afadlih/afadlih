from pathlib import Path
import importlib.util
import json
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE_PATH=ROOT/'scripts'/'update_repository_activity.py'
spec=importlib.util.spec_from_file_location('update_repository_activity',MODULE_PATH)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RepositoryActivityTests(unittest.TestCase):
    def setUp(self):
        self.sources=json.loads((ROOT/'portfolio'/'activity-sources.json').read_text(encoding='utf-8'))
        self.fixture=json.loads((ROOT/'tests'/'fixtures'/'repository-api.json').read_text(encoding='utf-8'))

    def test_snapshot_is_sorted_and_limited(self):
        snapshot=module.build_snapshot(self.sources,fixture=self.fixture)
        self.assertEqual(5,len(snapshot['items']))
        dates=[item['pushed_at'] for item in snapshot['items']]
        self.assertEqual(sorted(dates,reverse=True),dates)
        self.assertEqual('2026-08-04T23:42:15Z',snapshot['as_of'])
        self.assertEqual('afadlih/afadlih',snapshot['items'][0]['repository'])
        self.assertEqual(dates[0],snapshot['as_of'])

    def test_snapshot_excludes_private_or_archived_repository(self):
        fixture=json.loads(json.dumps(self.fixture))
        fixture['repositories']['afadlih/smart-clothesline-iot-system']['private']=True
        snapshot=module.build_snapshot(self.sources,fixture=fixture)
        repos={item['repository'] for item in snapshot['items']}
        self.assertNotIn('afadlih/smart-clothesline-iot-system',repos)

    def test_writer_does_not_change_identical_content(self):
        snapshot=module.build_snapshot(self.sources,fixture=self.fixture)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'activity.json'
            self.assertTrue(module.write_json_if_changed(path,snapshot))
            self.assertFalse(module.write_json_if_changed(path,snapshot))

    def test_cli_accepts_precreated_empty_output_file(self):
        import subprocess
        import sys

        with tempfile.NamedTemporaryFile(suffix='.json') as handle:
            result=subprocess.run(
                [
                    sys.executable,
                    str(ROOT/'scripts'/'update_repository_activity.py'),
                    '--fixture',
                    str(ROOT/'tests'/'fixtures'/'repository-api.json'),
                    '--write',
                    '--output',
                    handle.name,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0,result.returncode,result.stderr)
            payload=json.loads(Path(handle.name).read_text(encoding='utf-8'))
            self.assertTrue(payload['items'])

if __name__=='__main__': unittest.main()
