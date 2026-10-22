from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


class HelperTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture_home = self.root / 'home with spaces and "quotes"'
        self.fixture_home.mkdir()
        self.fake_bin = self.root / 'bin'
        self.fake_bin.mkdir()
        self.env = dict(os.environ, HOME=str(self.fixture_home),
                        PATH=str(self.fake_bin) + os.pathsep + os.environ['PATH'])

    def run_helper(self, name, *args):
        return subprocess.run([str(REPO / 'bin' / name), *map(str, args)],
                              env=self.env, capture_output=True, text=True,
                              timeout=10)


class FuddTests(HelperTest):
    def setUp(self):
        super().setUp()
        self.derived = self.fixture_home / 'Library/Developer/Xcode/DerivedData'
        self.trash = self.fixture_home / '.Trash'
        self.trash.mkdir()
        self.unrelated = self.trash / 'keep me.txt'
        self.unrelated.write_text('unrelated file')
        self.log = self.root / 'osascript.json'
        self.env['OSASCRIPT_LOG'] = str(self.log)
        stub = self.fake_bin / 'osascript'
        stub.write_text('#!' + sys.executable + '\n' + '''from pathlib import Path
import json, os, shutil, sys
script = sys.stdin.read()
Path(os.environ['OSASCRIPT_LOG']).write_text(json.dumps({'args': sys.argv[1:], 'script': script}))
if os.environ.get('OSASCRIPT_FAIL'):
    sys.exit(42)
if 'empty trash' in script.lower() or '-e' in sys.argv:
    sys.exit(43)
shutil.move(sys.argv[-1], str(Path(os.environ['HOME']) / '.Trash' / 'DerivedData'))
''')
        stub.chmod(0o755)

    def test_trashes_only_derived_data_with_quoted_home_path(self):
        self.derived.mkdir(parents=True)
        (self.derived / 'build.dat').write_text('build cache')
        result = self.run_helper('fudd')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.derived.exists())
        self.assertEqual((self.trash / 'DerivedData/build.dat').read_text(), 'build cache')
        self.assertEqual(self.unrelated.read_text(), 'unrelated file')
        request = json.loads(self.log.read_text())
        self.assertEqual(request['args'], ['-', str(self.derived)])
        self.assertNotIn('empty trash', request['script'].lower())

    def test_missing_directory_is_a_noop(self):
        result = self.run_helper('fudd')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.log.exists())
        self.assertTrue(self.unrelated.exists())

    def test_finder_failure_is_reported(self):
        self.derived.mkdir(parents=True)
        self.env['OSASCRIPT_FAIL'] = '1'
        result = self.run_helper('fudd')
        self.assertEqual(result.returncode, 42)
        self.assertTrue(self.derived.exists())
        self.assertNotIn('Moved', result.stdout)

    def test_refuses_to_follow_a_derived_data_symlink(self):
        external = self.root / 'external'
        external.mkdir()
        self.derived.parent.mkdir(parents=True)
        self.derived.symlink_to(external)
        result = self.run_helper('fudd')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.derived.is_symlink())
        self.assertFalse(self.log.exists())


if __name__ == '__main__':
    unittest.main()
