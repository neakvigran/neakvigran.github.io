"""Regression checks for opt-in math; uses only temporary vaults."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import yaml

SPEC = importlib.util.spec_from_file_location('publisher', Path(__file__).with_name('publish_obsidian.py'))
publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publisher)


class MathTests(unittest.TestCase):
    def test_inline_and_symbols(self):
        self.assertEqual(publisher.prepare_math(r'The value is $x\geq2$, and \(y\leq5\).'),
                         r'The value is $$x\geq2$$, and $$y\leq5$$.')
        formula = r'$$a \neq b,\quad \alpha \leq 10,\quad y \geq 5$$'
        self.assertEqual(publisher.prepare_math(formula), formula)

    def test_display(self):
        text = '$$\nf(x) = w \\cdot x + b\n$$'
        self.assertEqual(publisher.prepare_math(text), text)
        self.assertEqual(publisher.prepare_math(r'\[x\geq2\]'), '\n\n$$\nx\\geq2\n$$\n\n')

    def test_currency_and_variables(self):
        for text in ['$25 and $10.', '$25.50 and $10.00.', '$1,000 and $2,000.',
                     r'Escaped \$x\$ and \$25.', '$HOME and $PATH', 'an unmatched $x',
                     '$$unclosed', '$ x $', 'cost $ 25 and $ 10']:
            with self.subTest(text=text):
                self.assertEqual(publisher.prepare_math(text), text)
        self.assertEqual(publisher.prepare_math('$x$ costs $25 and $10.'),
                         '$$x$$ costs $25 and $10.')

    def test_code(self):
        for text in ['```python\nx = "$x$"\n```\n', '~~~~\n$x$\n~~~~\n',
                     '> ```\n> $x$\n> ```\n', '- ```\n  $x$\n  ```\n', '    code = "$x$"\n',
                     '`$x$`', '`` `$x$` ``', '`multiline\n$x$`',
                     '```unclosed\n$x$']:
            with self.subTest(text=text):
                self.assertEqual(publisher.prepare_math(text), text)

    def test_transform_idempotent(self):
        text = r'Inline $x$ and \(y\); display \[z\] costs $25 and $10.'
        once = publisher.prepare_math(text)
        self.assertEqual(publisher.prepare_math(once), once)

    def test_numeric_leading_inline(self):
        # Exact expressions from 2warm, Warmed Up, and convertme.py.
        expressions = [
            '32 + 8 + 2 = 42',
            r'3 \times 16 + 13 = 61',
            '62 = 32 + 16 + 8 + 4 + 2',
            '2^8', '2x + 3', r'2 \geq 1', r'2\pi', r'2 + \frac{1}{2}',
        ]
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assertEqual(publisher.prepare_math('$' + expression + '$'),
                                 '$$' + expression + '$$')

    def test_numeric_leading_display(self):
        for expression in ['32 + 8 + 2 = 42', r'3 \times 16 + 13 = 61', '62 = 32 + 16 + 8 + 4 + 2']:
            text = '$$\n' + expression + '\n$$'
            self.assertEqual(publisher.prepare_math(text), text)

    def test_numeric_currency_and_prose(self):
        for text in [
            '$25', '$100', 'The price is $25.', '$25 and $100.',
            '$25.50 and $100.00.', '$1,000 and $2,500.', '$25 + $100.',
            'Equipment costs $25 and service costs $10.', '$25$', '$100$',
            '$25 USD$', '$25 and shipping costs $', '$25 plus tax$',
            '$25.00 each; $100.00 total.', 'The price is $25\nand shipping is $10.',
        ]:
            with self.subTest(text=text):
                self.assertEqual(publisher.prepare_math(text), text)

    def test_numeric_code_and_escapes(self):
        for text in [
            '```python\nvalue = "$2^8$"\n```\n',
            '~~~bash\necho "$2^8$"\n~~~\n',
            '    value = "$2^8$"\n', '`$2^8$`', '`` `$2^8$` ``',
            r'Escaped \$2^8\$; escaped \$25.',
        ]:
            with self.subTest(text=text):
                self.assertEqual(publisher.prepare_math(text), text)

    def test_numeric_mixed_text(self):
        text = r'At $25 each, $2^8$ items satisfy $x \geq 2$; service costs $100.'
        expected = r'At $25 each, $$2^8$$ items satisfy $$x \geq 2$$; service costs $100.'
        self.assertEqual(publisher.prepare_math(text), expected)
        text = '$25, equation $32 + 8 + 2 = 42$, and shipping $10.'
        self.assertEqual(publisher.prepare_math(text),
                         '$25, equation $$32 + 8 + 2 = 42$$, and shipping $10.')

    def test_numeric_transform_idempotent(self):
        text = r'Math $2^8$ and $3 \times 16 + 13 = 61$ costs $25 and $100.'
        once = publisher.prepare_math(text)
        self.assertEqual(publisher.prepare_math(once), once)

    def test_metadata_boolean(self):
        self.assertIs(publisher.read_obsidian_metadata('---\nmath: true\n---\n')['math'], True)
        self.assertIs(publisher.read_obsidian_metadata('---\nmath: false\n---\n')['math'], False)
        for value in ['"true"','"false"','null','1','[true]']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                publisher.read_obsidian_metadata('---\nmath: '+value+'\n---\n')

    def test_frontmatter(self):
        raw=publisher.frontmatter('Title','2026-01-01','Category',['tag'],'Description',True)
        props=yaml.safe_load(raw.split('---')[1])
        self.assertIs(props['math'],True)
        self.assertEqual(raw.count('math:'),1)
        self.assertNotIn('math:',publisher.frontmatter('Title','2026-01-01','Category',['tag']))

    def test_obsidian_image_alignment_conversion(self):
        body, images, unresolved, warnings = publisher.convert(
            'Before\n![[shot.png|left]]\nAfter\n![[other.png|right]]',
            'room', {}
        )
        self.assertIn('![shot](/assets/img/obsidian/room/shot.png){: .obsidian-image-left }', body)
        self.assertIn('![other](/assets/img/obsidian/room/other.png){: .obsidian-image-right }', body)
        self.assertEqual(set(images), {'shot.png', 'other.png'})
        self.assertEqual(unresolved, [])
        self.assertEqual(warnings, [])

    def test_embedded_images_are_separate_markdown_blocks(self):
        body, _, _, _ = publisher.convert(
            'Intro\n![[left.png|left]]\nShort explanation.\n## Next heading\n'
            '![[plain.png]]\nFollowing paragraph.',
            'room', {}
        )
        self.assertRegex(body, r'\n{2,}!\[left\]\(/assets/img/obsidian/room/left\.png\)\{: \.obsidian-image-left \}\n{2,}Short explanation\.')
        self.assertRegex(body, r'\n{2,}!\[plain\]\(/assets/img/obsidian/room/plain\.png\)\n{2,}Following paragraph\.')

    def test_inline_image_embed_keeps_inline_position(self):
        body, _, _, _ = publisher.convert(
            'Text before ![[inline.png]] and after.', 'room', {}
        )
        self.assertEqual(
            body,
            'Text before ![inline](/assets/img/obsidian/room/inline.png) and after.'
        )

    def test_unmodified_image_conversion_and_unknown_modifier_warning(self):
        body, images, _, warnings = publisher.convert(
            '![[ordinary image.png]]\n![[wide.png|300]]', 'room', {}
        )
        self.assertIn('![ordinary image](/assets/img/obsidian/room/ordinary%20image.png)', body)
        self.assertNotIn('obsidian-image-', body)
        self.assertIn('![wide](/assets/img/obsidian/room/wide.png)', body)
        self.assertEqual(warnings, ['300'])
        self.assertEqual(set(images), {'ordinary image.png', 'wide.png'})

    def test_image_modifier_cannot_inject_html(self):
        body, _, _, warnings = publisher.convert(
            '![[shot.png|left<img src=x onerror=alert(1)>]]', 'room', {}
        )
        self.assertNotIn('<img', body)
        self.assertNotIn('onerror', body)
        self.assertEqual(warnings, ['left<img src=x onerror=alert(1)>'])

    def test_convert_preserves_code_inline_math_lists_and_tables(self):
        source = ('```text\n$cost 25\n  indented\n\nend\n```\n'
                  '`inline` and $2^8$\n\n- item\n\n| a | b |\n|---|---|\n| 1 | 2 |')
        converted, images, _, _ = publisher.convert(source, 'room', {})
        self.assertEqual(converted, source)
        self.assertEqual(images, {})
        self.assertEqual(publisher.prepare_math(converted), converted.replace('$2^8$', '$$2^8$$'))


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.vault=Path(self.temp.name)/'vault'
        self.repo=self.vault/'site'
        (self.repo/'tools').mkdir(parents=True)
        for name in ['publish_obsidian.py','publish-writeup','verify_writeup.py']:
            shutil.copy2(Path(__file__).with_name(name),self.repo/'tools'/name)
        self.env={**os.environ,'OBSIDIAN_VAULT':str(self.vault),'CHIRPY_REPO':str(self.repo),
                  'PYTHONDONTWRITEBYTECODE':'1'}

    def note(self,name,text):
        p=self.vault/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        return p

    def run_cli(self,*args,ok=True):
        p=subprocess.run(['bash',str(self.repo/'tools/publish-writeup'),*args],env=self.env,
                         text=True,capture_output=True)
        if ok:self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        else:self.assertNotEqual(p.returncode,0,p.stdout+p.stderr)
        return p

    def test_platforms_updates_and_idempotency(self):
        for platform in ['TryHackMe','HackTheBox','CyLab(picoCTF)']:
            key=platform+'/AI/'+platform+'.md'
            note=self.note(key,'---\nmath: true\ndescription: Keep me\ntags: [Easy, AI]\n---\n$x$ costs $25 and $10.\n')
            self.run_cli(key,'--write')
            manifest=json.loads((self.repo/'tools/.obsidian-published.json').read_text())
            post=self.repo/manifest[key]['post'];first=post.read_bytes()
            self.assertIn(b'math: true',first);self.assertIn(b'$$x$$ costs $25 and $10.',first)
            self.run_cli(key,'--write');self.assertEqual(first,post.read_bytes())
            props=yaml.safe_load(first.decode().split('---')[1])
            self.assertEqual(props['description'],'Keep me');self.assertEqual(props['tags'],['easy','ai'])
            self.assertEqual(props['categories'],[platform,'AI'])
            # Explicit false disables both normalization and rendering.
            note.write_text(note.read_text().replace('math: true','math: false'))
            self.run_cli(key,'--write');self.assertIn(b'math: false',post.read_bytes())
            self.assertIn(b'$x$ costs $25 and $10.',post.read_bytes())
            p=subprocess.run(['python3',str(self.repo/'tools/verify_writeup.py'),str(note)],env=self.env,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)

    def test_existing_opt_in_and_nonmath(self):
        key='TryHackMe/Challenge/ordinary.md';p=self.note(key,'---\ndescription: Keep\ntags: [Easy]\n---\n`$x$` and $25 and $10.\n')
        self.run_cli(key,'--write');m=json.loads((self.repo/'tools/.obsidian-published.json').read_text());post=self.repo/m[key]['post']
        first=post.read_bytes();self.assertNotIn(b'math:',first)
        self.run_cli(key,'--write');self.assertEqual(post.read_bytes(),first)
        # An existing post-level opt-in is retained when source metadata is absent.
        post.write_text(post.read_text().replace('toc: true','math: true\ntoc: true'))
        self.run_cli(key,'--write');self.assertIn(b'math: true',post.read_bytes())

    def test_numeric_platform_publishing_and_opt_in(self):
        for platform in ['TryHackMe', 'HackTheBox', 'CyLab(picoCTF)']:
            key = platform + '/General Skill/numeric-' + platform + '.md'
            content = '$32 + 8 + 2 = 42$; equipment $25, service $100.\n'
            original = '---\nmath: true\ndescription: Preserve\ntags: [Easy]\n---\n' + content
            note = self.note(key, original)
            self.run_cli(key, '--write')
            manifest_path = self.repo / 'tools/.obsidian-published.json'
            manifest = json.loads(manifest_path.read_text())
            post = self.repo / manifest[key]['post']
            first = post.read_bytes()
            self.assertIn(b'$$32 + 8 + 2 = 42$$; equipment $25, service $100.', first)
            first_manifest = manifest_path.read_bytes()
            self.run_cli(key, '--write')
            self.assertEqual(post.read_bytes(), first)
            self.assertEqual(manifest_path.read_bytes(), first_manifest)
            self.assertEqual(note.read_text(), original)
            for metadata in ['---\nmath: false\n---\n', '']:
                note.write_text(metadata + content)
                # Removing source math must also remove a prior post-level opt-in
                # for this absent-opt-in test; test each as a fresh publication.
                if not metadata:
                    key = platform + '/General Skill/absent-' + platform + '.md'
                    note = self.note(key, content)
                self.run_cli(key, '--write')
                manifest = json.loads(manifest_path.read_text())
                output = (self.repo / manifest[key]['post']).read_text()
                self.assertIn(content, output)

    def test_caesar_and_new_caesar(self):
        (self.repo / '_posts').mkdir()
        (self.repo / '_posts/2020-01-01-new-caesar.md').write_text('Existing New Caesar')
        key = 'CyLab(picoCTF)/Cryptography/caesar.md'
        self.note(key, 'Ordinary text')
        self.run_cli(key, '--write')
        key = 'CyLab(picoCTF)/Cryptography/New Caesar.md'
        self.note(key, 'Ordinary text')
        self.assertIn('Post already exists', self.run_cli(key, ok=False).stderr)

    def test_slug_collisions(self):
        # A suffix is not an exact slug collision.
        (self.repo/'_posts').mkdir()
        (self.repo/'_posts/2020-01-01-my-cat.md').write_text('Existing suffix')
        key='CyLab(picoCTF)/General Skill/cat.md';self.note(key,'ordinary')
        self.run_cli(key,'--write')
        # Another platform cannot steal an already registered slug.
        other='TryHackMe/Challenge/cat.md';self.note(other,'ordinary')
        self.run_cli(other,ok=False)
        # Unregistered exact slug, even with a different date, must be rejected.
        (self.repo/'_posts/2020-01-01-unique.md').write_text('Existing exact slug')
        key='CyLab(picoCTF)/General Skill/unique.md';self.note(key,'ordinary')
        self.assertIn('Post already exists',self.run_cli(key,ok=False).stderr)

    def test_date_metadata_lifecycle_and_validation(self):
        key='TryHackMe/Challenge/dates.md'
        note=self.note(key,'---\ndate: 2024-02-29\nlast_modified_at: "2026-11-08"\n---\nBody stays.\n')
        self.run_cli(key,'--write')
        mp=self.repo/'tools/.obsidian-published.json'; manifest=json.loads(mp.read_text())
        post=self.repo/manifest[key]['post']; slug=manifest[key]['slug']; postpath=manifest[key]['post']
        props=yaml.safe_load(post.read_text().split('---')[1])
        self.assertEqual(props['date'].isoformat(),'2024-02-29')
        self.assertEqual(props['last_modified_at'].isoformat(),'2026-11-08')
        self.assertEqual(manifest[key]['last_modified_at'],'2026-11-08')
        note.write_text('---\ndate: 2025-01-02\n---\nBody stays.\n')
        self.run_cli(key,'--write')
        manifest=json.loads(mp.read_text());props=yaml.safe_load(post.read_text().split('---')[1])
        self.assertEqual(props['date'].isoformat(),'2025-01-02')
        self.assertEqual(props['last_modified_at'].isoformat(),'2026-11-08')
        self.assertEqual(manifest[key]['post'],postpath);self.assertEqual(manifest[key]['slug'],slug)
        note.write_text('---\ndate: 2025-01-02\nlast_modified_at: null\n---\nBody stays.\n')
        self.run_cli(key,'--write')
        manifest=json.loads(mp.read_text());self.assertNotIn('last_modified_at',manifest[key])
        self.assertNotIn('last_modified_at:',post.read_text())
        before=(post.read_bytes(),mp.read_bytes())
        for val in ['2026-02-29','2026-13-01','2026-04-31','2026-11-08 14:00:00','"2026-11-08T10:30:00+07:00"','123']:
            note.write_text('---\ndate: '+val+'\n---\nChanged body\n')
            self.run_cli(key,'--write',ok=False)
            self.assertEqual((post.read_bytes(),mp.read_bytes()),before)


if __name__=='__main__':unittest.main()
