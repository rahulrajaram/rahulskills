"""Offline embedding invariants; browser rendering is a separate check."""

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_viewer.py")
SPEC = importlib.util.spec_from_file_location("build_viewer", SCRIPT)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.current_script = None
        self.attributes = []

    def handle_starttag(self, tag, attrs):
        self.attributes.extend(attrs)
        if tag == "script":
            self.current_script = {"attrs": dict(attrs), "text": ""}
            self.scripts.append(self.current_script)

    def handle_data(self, data):
        if self.current_script is not None:
            self.current_script["text"] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.current_script = None


class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.config = {"title": 'A "quoted" <title>', "summary": "Summary",
                       "boundary": "Draft only", "revision": "v1 pending"}
        self.template = builder.TEMPLATE.read_text()

    def test_contexts_preserve_source_without_markup_injection(self):
        source = b'flowchart TB\r\n A["</script> \\path {{BADGE}} source"]\r\n'
        config = dict(self.config, summary='<img src=x onerror="bad()"> {{BADGE}}',
                      sections=[{"title": "</summary>", "paragraphs": ["<script>bad()</script>"]}])
        document, digest = builder.build(source, config, 'file:///tmp/a"b.js', self.template)
        parsed = Document()
        parsed.feed(document)
        self.assertEqual(len(parsed.scripts), 3)
        embedded = next(s for s in parsed.scripts if s["attrs"].get("id") == "diagram-source")
        self.assertEqual(json.loads(embedded["text"]).encode(), source)
        self.assertEqual(digest, hashlib.sha256(source).hexdigest())
        self.assertIn(('aria-label', config['title']), parsed.attributes)
        self.assertFalse(any(key.startswith('on') for key, _ in parsed.attributes))
        self.assertIn('{{BADGE}}', document)
        self.assertNotIn('</script> \\path', document)

    def test_digest_and_template_mismatch_refused(self):
        with self.assertRaises(ValueError):
            builder.build(b'flowchart TB', dict(self.config, expected_digest='0' * 64),
                          'file:///tmp/mermaid.js', self.template)
        for template in (self.template + '{{UNKNOWN}}', self.template + '{{BADGE}}',
                         self.template.replace('{{BADGE}}', '')):
            with self.subTest(template=template[-30:]), self.assertRaises(ValueError):
                builder.build(b'flowchart TB', self.config, 'file:///tmp/mermaid.js', template)

    def test_nonlocal_runtime_uri_is_refused(self):
        with self.assertRaises(ValueError):
            builder.build(b'flowchart TB', self.config, 'https://example.test/mermaid.js', self.template)

    def test_cli_preserves_inputs_and_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, config, runtime, output = [root / name for name in
                                             ('diagram.mmd', 'config.json', 'mermaid.js', 'viewer.html')]
            source.write_text('flowchart TB\n A --> B\n')
            config.write_text(json.dumps(self.config))
            runtime.write_text('// inert fixture; never loaded')
            command = [sys.executable, str(SCRIPT), '--source', str(source), '--config', str(config),
                       '--runtime', str(runtime), '--out', str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = output.read_bytes()
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual(output.read_bytes(), original)
            overwritten_input = command[:-1] + [str(source), '--replace']
            self.assertEqual(subprocess.run(overwritten_input, capture_output=True).returncode, 2)
            self.assertEqual(source.read_text(), 'flowchart TB\n A --> B\n')


if __name__ == '__main__':
    unittest.main()
