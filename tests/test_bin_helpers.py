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
                        PATH=str(self.fake_bin) + os.pathsep + os.defpath)

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
shutil.move(sys.argv[-1], str(Path(os.environ['HOME']) / '.Trash' / 'DerivedData'))
if 'empty trash' in script.lower():
    if os.environ.get('OSASCRIPT_EMPTY_FAIL'):
        sys.exit(44)
    for item in (Path(os.environ['HOME']) / '.Trash').iterdir():
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            item.unlink()
''')
        stub.chmod(0o755)

    def test_trashes_derived_data_then_empties_the_entire_trash(self):
        self.derived.mkdir(parents=True)
        (self.derived / 'build.dat').write_text('build cache')
        result = self.run_helper('fudd')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.derived.exists())
        self.assertEqual(list(self.trash.iterdir()), [])
        request = json.loads(self.log.read_text())
        self.assertEqual(request['args'], ['-', str(self.derived)])
        self.assertLess(request['script'].index('move (POSIX file'),
                        request['script'].index('empty trash'))
        self.assertIn('emptied the Trash', result.stdout)

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
        self.assertTrue(self.unrelated.exists())
        self.assertNotIn('Moved', result.stdout)

    def test_emptying_failure_is_reported_after_trashing(self):
        self.derived.mkdir(parents=True)
        self.env['OSASCRIPT_EMPTY_FAIL'] = '1'
        result = self.run_helper('fudd')
        self.assertEqual(result.returncode, 44)
        self.assertFalse(self.derived.exists())
        self.assertTrue((self.trash / 'DerivedData').is_dir())
        self.assertTrue(self.unrelated.exists())
        self.assertNotIn('emptied', result.stdout)

    def test_help_explains_that_the_entire_trash_is_emptied(self):
        result = self.run_helper('fudd', '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('entire Trash', result.stdout)
        self.assertFalse(self.log.exists())

    def test_refuses_to_follow_a_derived_data_symlink(self):
        external = self.root / 'external'
        external.mkdir()
        self.derived.parent.mkdir(parents=True)
        self.derived.symlink_to(external)
        result = self.run_helper('fudd')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.derived.is_symlink())
        self.assertFalse(self.log.exists())


class FuspmTests(HelperTest):
    def setUp(self):
        super().setUp()
        self.cache = self.fixture_home / 'Library/Caches/org.swift.swiftpm'
        self.config = self.fixture_home / 'Library/org.swift.swiftpm'
        self.config.mkdir(parents=True)
        (self.config / 'keep.json').write_text('settings')

    def run_cache_cleanup(self):
        return subprocess.run(['/bin/bash', str(REPO / 'bin/fuspm')], env=self.env,
                              capture_output=True, text=True, timeout=10)

    def test_removes_only_the_cache_with_quoted_home_path(self):
        self.cache.mkdir(parents=True)
        (self.cache / 'artifact').write_text('cached artifact')
        result = self.run_cache_cleanup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.cache.exists())
        self.assertEqual((self.config / 'keep.json').read_text(), 'settings')

    def test_missing_cache_is_a_noop(self):
        result = self.run_cache_cleanup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.cache.exists())
        self.assertTrue(self.config.exists())

    def test_removes_a_cache_symlink_without_following_it(self):
        external = self.root / 'external'
        external.mkdir()
        (external / 'keep').write_text('outside cache')
        self.cache.parent.mkdir(parents=True)
        self.cache.symlink_to(external)
        result = self.run_cache_cleanup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.cache.is_symlink())
        self.assertEqual((external / 'keep').read_text(), 'outside cache')

    def test_reports_removal_failure(self):
        self.cache.mkdir(parents=True)
        stub = self.fake_bin / 'rm'
        stub.write_text('#!/bin/sh\nexit 42\n')
        stub.chmod(0o755)
        result = self.run_cache_cleanup()
        self.assertEqual(result.returncode, 42)
        self.assertTrue(self.cache.exists())


class TouchIDTests(HelperTest):
    def setUp(self):
        super().setUp()
        self.pam = self.root / 'pam directory'
        self.pam.mkdir()
        self.vendor = self.pam / 'sudo'
        self.vendor.write_text('auth include sudo_local\nauth required pam_opendirectory.so\n')
        self.template = self.pam / 'sudo_local.template'
        self.template.write_text('# Local configuration\n#auth sufficient pam_tid.so\n')
        self.target = self.pam / 'sudo_local'

    def enable(self, *args):
        return self.run_helper('enable-tid-sudo', '--pam-dir', self.pam, *args)

    def test_creates_local_config_without_changing_vendor_files(self):
        vendor = self.vendor.read_bytes()
        template = self.template.read_bytes()
        result = self.enable()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.read_text(), '# Local configuration\nauth sufficient pam_tid.so\n')
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o644)
        self.assertEqual(self.vendor.read_bytes(), vendor)
        self.assertEqual(self.template.read_bytes(), template)

    def test_preserves_custom_rules_and_backs_up_existing_file(self):
        original = 'auth optional /opt/homebrew/lib/pam/pam_reattach.so\n#auth sufficient pam_tid.so\naccount optional pam_permit.so\n'
        self.target.write_text(original)
        result = self.enable()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.read_text(), original.replace('#auth', 'auth'))
        backups = list(self.pam.glob('sudo_local.before-touch-id.*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), original)

    def test_appends_touch_id_when_no_commented_rule_exists(self):
        self.target.write_text('auth optional pam_reattach.so')
        result = self.enable()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.read_text(), 'auth optional pam_reattach.so\nauth sufficient pam_tid.so\n')

    def test_repeated_runs_do_not_rewrite_or_duplicate_the_rule(self):
        self.assertEqual(self.enable().returncode, 0)
        before = self.target.stat()
        result = self.enable()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.stat().st_ino, before.st_ino)
        self.assertEqual(self.target.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(list(self.pam.glob('sudo_local.before-touch-id.*')), [])

    def test_check_reports_state_without_writing(self):
        result = self.enable('--check')
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.target.exists())
        self.assertEqual(self.enable().returncode, 0)
        self.assertEqual(self.enable('--check').returncode, 0)

    def test_refuses_unsupported_vendor_configuration(self):
        self.vendor.write_text('auth required pam_opendirectory.so\n')
        result = self.enable()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.pam.glob('.sudo_local.*')), [])

    def test_refuses_to_overwrite_a_symlink(self):
        outside = self.root / 'outside'
        outside.write_text('untouched')
        self.target.symlink_to(outside)
        result = self.enable()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(outside.read_text(), 'untouched')

    def test_preserves_a_custom_active_touch_id_rule(self):
        original = 'auth required pam_tid.so\n'
        self.target.write_text(original)
        result = self.enable()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.target.read_text(), original)
        self.assertEqual(list(self.pam.glob('sudo_local.before-touch-id.*')), [])


if __name__ == '__main__':
    unittest.main()
