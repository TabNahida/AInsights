const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, '../docs/app.js'), 'utf8');
const names = ['radarAxes', 'radarBoardProfile', 'radarAxisValue', 'radarHasData',
  'radarLinePath', 'radarPolygonPoints', 'radarPoint', 'radarProfilePopulation',
  'radarAxisAverage', 'modelForRankingGrain', 'benchmarkMatchesSearch',
  'benchmarkRankingRows', 'benchmarkHref', 'radarVisionOptions', 'radarAxisRank',
  'handleCustomAction', 'activeCustomWeights', 'restoreActiveCustomDefaults',
  'modelVisionResults', 'renderVisionAvailability', 'radarVisionComparisonGroup', 'radarVisionCohortValues'];
const context = vm.createContext({
  state: { data: { models: [] }, dedupe: true },
  tr: (key) => key,
  escapeHtml: (value) => String(value),
  formatNumber: (value) => String(value),
  clamp: (value, min, max) => Math.min(max, Math.max(min, value)),
  formatSvgNumber: (value) => value.toFixed(2),
  URLSearchParams,
  location: { search: '' },
});
for (const name of names) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start >= 0, name);
  const end = source.indexOf('\nfunction ', start + 1);
  vm.runInContext(source.slice(start, end === -1 ? undefined : end), context);
}

test('vision uses the observed AA score and preserves zero and missing values', () => {
  const axis = context.radarAxes().at(-1);
  assert.equal(axis.id, 'visual-understanding');
  assert.equal(context.radarAxisValue({ scores: { 'MMMU-Pro': 82.4 } }, axis), 82.4);
  assert.equal(context.radarAxisValue({ scores: { 'MMMU-Pro': 0 } }, axis), 0);
  for (const value of [undefined, null, '', NaN]) {
    assert.equal(context.radarAxisValue({ scores: { 'MMMU-Pro': value } }, axis), null);
  }
  assert.equal(context.radarAxisValue({ scores: { 'benchmark:mmmu-pro': 90 },
    rankingProfile: { extensionCoverageScore: 100 } }, axis), null);
});

test('missing vision retains other axes without drawing a fabricated zero or closed area', () => {
  const model = { rankingProfile: { boards: { coding: { score: 50 } } } };
  assert.equal(context.radarHasData(model), true);
  assert.equal(context.radarHasData({}), false);
  const values = [50, 60, 70, 80, 90, null];
  const center = { x: 100, y: 100 };
  assert.equal(context.radarPolygonPoints(values, center, 80), '');
  assert.equal((context.radarLinePath(values, center, 80).match(/M/g) || []).length, 4);
  assert.equal((context.radarLinePath([0, 60, 70, 80, 90, 95], center, 80).match(/M/g) || []).length, 6);
});

test('each axis average uses its own observed population and excludes unranked models', () => {
  context.state.data.models = [
    { rankingProfile: { boards: { coding: { score: 40 } } }, scores: { 'MMMU-Pro': 80 } },
    { rankingProfile: { boards: { coding: { score: 60 } } }, scores: {} },
    { rankingProfile: { boards: { coding: { score: 80 } } }, scores: { 'MMMU-Pro': 0 } },
    { scores: { 'MMMU-Pro': 100 } },
  ];
  const axes = context.radarAxes();
  assert.equal(context.radarAxisAverage(axes[0]), 60);
  assert.equal(context.radarAxisAverage(axes.at(-1)), 40);
});

test('search normalizes case, spaces and full-width text and searches across fields', () => {
  assert.equal(context.benchmarkMatchesSearch('  ＧＰＴ OpenAI ', ['GPT-6', 'OpenAI']), true);
  assert.equal(context.benchmarkMatchesSearch('视觉', ['视觉理解', 'MMMU-Pro']), true);
  assert.equal(context.benchmarkMatchesSearch('', ['anything']), true);
  assert.equal(context.benchmarkMatchesSearch('Gemini', ['GPT-6', 'OpenAI']), false);
});

test('model filtering keeps competition ranks, ties and measured zero scores', () => {
  context.state.data.models = [
    { model: 'Alpha', scores: { test: 90 } },
    { model: 'Beta', scores: { test: 80 } },
    { model: 'Beta tied', scores: { test: 80 } },
    { model: 'Beta zero', scores: { test: 0 } },
    { model: 'Missing', scores: {} },
  ];
  const rows = context.benchmarkRankingRows({ key: 'test' });
  const filtered = rows.filter(row => context.benchmarkMatchesSearch('beta', [row.model.model]));
  assert.deepEqual(Array.from(filtered, row => row.rank), [2, 2, 4]);
  assert.equal(filtered.at(-1).value, 0);
});

test('benchmark navigation retains both searches with correctly encoded URLs', () => {
  context.location.search = '?id=old&benchmarkSearch=MMMU&modelSearch=Claude+%26+GPT';
  const result = new URL(context.benchmarkHref('benchmark:mmmu-pro'), 'https://example.org');
  assert.equal(result.searchParams.get('id'), 'benchmark:mmmu-pro');
  assert.equal(result.searchParams.get('benchmarkSearch'), 'MMMU');
  assert.equal(result.searchParams.get('modelSearch'), 'Claude & GPT');
});

test('visual selection keeps one benchmark and does not substitute another test or tier', () => {
  const official = { benchmarkId: 'mmmu', label: 'MMMU', value: 72, exactConfiguration: true };
  const model = { scores: {}, visionBenchmarks: [official, { benchmarkId: 'charxiv-no-tools', value: 85, exactConfiguration: false }] };
  const axis = { visionBenchmark: 'mmmu' };
  assert.equal(context.radarAxisValue(model, axis), 72);
  assert.equal(context.radarAxisValue(model, { visionBenchmark: 'mmmu-pro' }), null);
  assert.equal(context.radarAxisValue(model, { visionBenchmark: 'charxiv-no-tools' }), null);
  assert.equal(context.radarAxisAverage(axis), null);
  assert.equal(context.radarAxisRank(axis, model), null);
  assert.equal(context.radarVisionOptions([model])[0].id, 'mmmu');
  assert.ok(!context.radarVisionOptions([model]).some(option => option.id === 'charxiv-no-tools'));
});

test('comparison selects the test with the most matching configurations and prefers AA on ties', () => {
  const official = { benchmarkId: 'mmmu', label: 'MMMU', value: 70, exactConfiguration: true };
  const a = { scores: { 'MMMU-Pro': 80 }, visionBenchmarks: [official] };
  const b = { scores: {}, visionBenchmarks: [official] };
  assert.equal(context.radarVisionOptions([a])[0].id, 'aa');
  assert.equal(context.radarVisionOptions([a, b])[0].id, 'mmmu');
});


test('restore keeps the benchmark preset and leaves other mode weights intact', () => {
  Object.assign(context, {
    customManualWeightPresetId: 'manual',
    customWeightsForPreset: () => ({ vision: 20, reasoning: 80 }),
    applyMissingModePreset: () => {},
    renderWeights: () => {},
    renderResults: () => {},
    els: { weightsGrid: { querySelector: () => ({ focus() {} }) } },
  });
  Object.assign(context.state, {
    customToolMode: 'benchmark-lab', customWeightPresetId: 'manual',
    customWeights: { vision: 0, reasoning: 0 },
    customMethodWeights: { rasch: 15 }, customBoardWeights: { coding: 35 },
    data: { presets: { custom: {} } },
  });
  context.handleCustomAction('restore');
  assert.equal(context.state.customWeightPresetId, 'benchmark-lab');
  assert.deepEqual(context.state.customWeights, { vision: 20, reasoning: 80 });
  assert.equal(context.state.customMethodWeights.rasch, 15);
  assert.equal(context.state.customBoardWeights.coding, 35);
  context.handleCustomAction('clear');
  assert.equal(context.state.customWeightPresetId, 'manual');
  assert.deepEqual(context.state.customWeights, { vision: 0, reasoning: 0 });
});


test('missing selected vision exposes tested alternatives without mixing comparison scores', () => {
  const fable = { model: 'Fable', scores: {}, visionBenchmarks: [
    { benchmarkId: 'chartography-no-tools', label: 'Chartography', value: 42.6, exactConfiguration: true },
  ] };
  const opus = { model: 'Opus', scores: { 'MMMU-Pro': 84.7 } };
  const html = context.renderVisionAvailability([fable, opus], 'aa');
  assert.match(html, /Fable/);
  assert.match(html, /data-vision-select="chartography-no-tools"/);
  assert.doesNotMatch(html, /<strong>Opus/);
  assert.equal(context.modelVisionResults(fable)[0].value, 42.6);
  assert.equal(context.radarAxisValue(fable, context.radarAxes().at(-1)), null);
  assert.equal(context.renderVisionAvailability([fable], 'chartography-no-tools'), '');
});

test('reference-only vision explains the missing configuration without a score switch', () => {
  const model = { model: 'Fable low', scores: {}, visionBenchmarks: [
    { benchmarkId: 'chartography-no-tools', label: 'Chartography', value: 42.6, exactConfiguration: false },
  ] };
  assert.equal(context.modelVisionResults(model).length, 0);
  const html = context.renderVisionAvailability([model], 'aa');
  assert.match(html, /visionReferenceOnly/);
  assert.doesNotMatch(html, /data-vision-select/);
});


test('Fable detail radar closes both model and same-protocol mean; AA defaults stay unchanged', () => {
  const payload = JSON.parse(fs.readFileSync(path.join(__dirname, '../docs/data/models.json'), 'utf8'));
  context.state.data = payload;
  context.state.dedupe = true;
  for (const [slug, score] of [['claude-fable-5', 36.6], ['claude-fable-5-1', 42.6]]) {
    const model = payload.models.find(row => row.slug === slug);
    const option = context.radarVisionOptions([model])[0];
    assert.equal(option.id, 'chartography-no-tools');
    const axes = context.radarAxes();
    axes[5] = { visionBenchmark: option.id, visionComparisonGroup: context.radarVisionComparisonGroup([model], option.id) };
    assert.equal(context.radarAxisValue(model, axes[5]), score);
    assert.equal(context.radarVisionCohortValues(axes[5]).length, 4);
    assert.ok(Math.abs(context.radarAxisAverage(axes[5]) - 31.2) < 1e-10);
    assert.equal(context.radarAxisRank(axes[5], model), null);
    assert.ok(context.radarPolygonPoints(axes.map(axis => context.radarAxisValue(model, axis)), {x: 100, y: 100}, 80));
    assert.ok(context.radarPolygonPoints(axes.map(axis => context.radarAxisAverage(axis)), {x: 100, y: 100}, 80));
    assert.ok(Math.abs(context.radarAxisAverage({ visionBenchmark: 'chartography-tools',
      visionComparisonGroup: context.radarVisionComparisonGroup([model], 'chartography-tools') }) - 81.3) < 1e-10);
  }
  for (const slug of ['gpt-6-astra', 'claude-opus-5']) {
    const model = payload.models.find(row => row.slug === slug);
    assert.ok(model, slug);
    assert.equal(context.radarVisionOptions([model])[0].id, 'aa');
    assert.equal(context.radarAxisValue(model, context.radarAxes()[5]), model.scores['MMMU-Pro']);
  }
});

test('official means exclude reference tiers, unrelated protocols and singleton cohorts', () => {
  const row = { benchmarkId: 'mmmu', exactConfiguration: true, comparisonGroup: 'same-protocol', value: 40 };
  const a = { slug: 'a', visionBenchmarks: [row] };
  const b = { slug: 'b', visionBenchmarks: [{...row, value: 60}] };
  const reference = {slug: 'reference', visionBenchmarks: [{...row, exactConfiguration: false, value: 99}]};
  const other = {slug: 'other', visionBenchmarks: [{...row, comparisonGroup: 'different', value: 100}]};
  const axis = {visionBenchmark: 'mmmu', visionComparisonGroup: 'same-protocol'};
  context.state.data = {models: [a, b, reference, other, a]};
  assert.equal(context.radarAxisAverage(axis), 50);
  assert.equal(context.radarVisionComparisonGroup([a, other], 'mmmu'), null);
  context.state.data = {models: [a, reference, other]};
  assert.equal(context.radarAxisAverage(axis), null);
});
