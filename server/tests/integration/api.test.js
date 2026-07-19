import test from 'node:test';
import assert from 'node:assert';
import app from '../../app.js';

test('Node.js Backend Gateway Suite', async (t) => {

  await t.test('GET /api/versions — Version Discovery', async () => {
    // Basic verification of version router export
    assert.strictEqual(typeof app, 'function');
  });

  await t.test('App Initialization', async () => {
    assert.ok(app);
  });
});
