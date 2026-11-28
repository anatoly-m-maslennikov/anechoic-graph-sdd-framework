import { strict as assert } from 'node:assert';
import { test } from 'node:test';
import { loadLib } from '../FEATURE_IWE_CONSOLE_FRONTEND__tests__shared.ts';
const { atomTextParts } = await loadLib();

test('splits Atom references without interpreting document markup', () => {
  const body = '<script> CA-SU-14 and AN-S-2@3-draft </script>';
  assert.deepEqual(atomTextParts(body), [
    { text: '<script> ' }, { text: 'CA-SU-14', ref: 'CA-SU-14' },
    { text: ' and ' }, { text: 'AN-S-2@3-draft', ref: 'AN-S-2@3-draft' },
    { text: ' </script>' },
  ]);
  assert.equal(atomTextParts(body).map((part) => part.text).join(''), body);
});

test('links the exact revision within canonical filenames', () => {
  const text = 'AN-S-1@2-SPEC--example.md and AN-S-1@3-draft-SPEC--example.md';
  assert.deepEqual(atomTextParts(text).flatMap(({ ref }) => ref ? [ref] : []),
    ['AN-S-1@2', 'AN-S-1@3-draft']);
  assert.equal(atomTextParts(text).map((part) => part.text).join(''), text);
});
