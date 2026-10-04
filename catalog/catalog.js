await customElements.whenDefined('model-viewer');
const ModelViewer = customElements.get('model-viewer');
const siteRoot = new URL('../', import.meta.url);
const staticSite = document.querySelector('meta[name="catalog-mode"]').content === 'static';
const catalogURL = new URL(document.querySelector('meta[name="catalog-endpoint"]').content, siteRoot);
ModelViewer.dracoDecoderLocation = new URL('catalog/vendor/draco/', siteRoot).href;
ModelViewer.ktx2TranscoderLocation = new URL('catalog/vendor/basis/', siteRoot).href;
ModelViewer.meshoptDecoderLocation = new URL('catalog/vendor/meshopt_decoder.js', siteRoot).href;
const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
const state = {q: params.get('q') || '', category: params.get('category') || '',
  animated: params.get('animated') === '1', asset: params.get('asset') || ''};
let catalog = null, active = null, viewer = null, changingClip = false, polling = false;
let clipGeneration = 0;
const number = value => value == null ? 'Unavailable' : value.toLocaleString();
const fileURL = file => new URL(file.path.split('/').map(encodeURIComponent).join('/'), siteRoot).href + '?v=' + encodeURIComponent(file.version);
const placeholderIcon = '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M32 4 57 18v28L32 60 7 46V18Z M7 18l25 14 25-14 M32 32v28 M32 4v28"/></svg>';

function text(tag, content, className) {
  const node = document.createElement(tag); node.textContent = content;
  if (className) node.className = className;
  return node;
}
function writeURL(push = false) {
  const url = new URL(location.href); url.search = '';
  for (const key of ['q', 'category', 'asset']) if (state[key]) url.searchParams.set(key, state[key]);
  if (state.animated) url.searchParams.set('animated', '1');
  history[push ? 'pushState' : 'replaceState'](null, '', url);
}
function applyFilters() {
  $('search').value = state.q; $('category').value = state.category;
  $('animated').checked = state.animated;
}
function imageIn(host, file, label, fallback) {
  host.replaceChildren();
  if (!file) { host.append(text('p', fallback)); return; }
  const img = new Image(); img.alt = label; img.loading = 'lazy'; img.src = fileURL(file);
  img.onerror = () => host.replaceChildren(text('p', fallback));
  host.append(img);
}
function renderGrid() {
  const assets = catalog.assets.filter(asset =>
    (!state.category || asset.category === state.category) &&
    (!state.animated || asset.animations.length > 0) &&
    `${asset.title} ${asset.id} ${asset.category}`.toLowerCase().includes(state.q.toLowerCase()));
  $('count').textContent = `${assets.length} of ${catalog.assets.length} exported assets`;
  $('empty').hidden = assets.length !== 0;
  // Keep unaffected cards (and their loaded thumbnails) during automatic refresh.
  const old = new Map([...$('grid').children].map(card => [card.dataset.id, card]));
  const nodes = assets.map(asset => {
    const signature = JSON.stringify(asset);
    if (old.get(asset.id)?.dataset.signature === signature) return old.get(asset.id);
    const card = document.createElement('button'); card.className = 'card';
    card.dataset.id = asset.id; card.dataset.signature = signature;
    card.setAttribute('aria-label', `Open ${asset.title}`);
    const media = document.createElement('div'); media.className = 'card-media';
    const fallback = text('div', '', 'placeholder');
    fallback.innerHTML = placeholderIcon; fallback.append(text('span', 'Thumbnail not rendered'));
    media.append(fallback);
    const file = asset.thumbnail || asset.preview;
    if (file) {
      const img = new Image(); img.alt = `${asset.title} preview`; img.loading = 'lazy';
      img.width = 480; img.height = 480;
      img.src = fileURL(file); img.onerror = () => img.remove(); media.append(img);
    }
    if (asset.animations.length) media.append(text('span', `${asset.animations.length} clips`, 'badge'));
    const caption = text('div', '', 'caption');
    caption.append(text('div', asset.category, 'tag'), text('strong', asset.title),
      text('small', `${number(asset.triangles)} triangles · ${number(asset.materials)} materials`));
    if (asset.error) caption.append(text('small', 'Export unavailable', 'warning'));
    card.append(media, caption); card.onclick = () => {state.asset = asset.id; writeURL(true); syncDetail();};
    return card;
  });
  $('grid').replaceChildren(...nodes);
}
function renderMetadata(asset) {
  $('asset-title').textContent = asset.title; $('asset-category').textContent = asset.category;
  $('stats').replaceChildren();
  for (const [label, value] of [['Triangles', number(asset.triangles)], ['Materials', number(asset.materials)],
    ['File size', asset.bytes == null ? 'Unavailable' : `${(asset.bytes / 1024).toLocaleString(undefined, {maximumFractionDigits: 1})} KiB`],
    ['Animations', asset.error ? 'Unavailable' : number(asset.animations.length)]]) $('stats').append(text('dt', label), text('dd', value));
  $('links').replaceChildren();
  for (const [file, label] of [[asset.source, 'Editable .blend'], [asset.model, 'Exported .glb']]) {
    if (file) { const a = text('a', label); a.href = fileURL(file); a.download = ''; $('links').append(a); }
    else $('links').append(text('span', asset.source_excluded ? 'Source download not published' : 'Source unavailable'));
  }
  imageIn($('preview'), asset.preview || asset.thumbnail, `${asset.title} render`, 'No rendered preview available');
  const ref = asset.reference;
  if (ref?.crop) {
    const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', ref.crop.join(' ')); svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', `${asset.title} reference`);
    const image = document.createElementNS(ns, 'image'); image.setAttribute('href', fileURL(ref));
    // Natural image dimensions preserve the original pixel coordinate crop.
    const probe = new Image(); probe.onload = () => {
      image.setAttribute('width', probe.naturalWidth); image.setAttribute('height', probe.naturalHeight);
    };
    probe.onerror = () => {if ($('reference').contains(svg)) $('reference').replaceChildren(text('p', 'Reference unavailable'));};
    probe.src = fileURL(ref); svg.append(image); $('reference').replaceChildren(svg);
  } else imageIn($('reference'), ref, `${asset.title} reference`, 'No reference associated');
  $('asset-message').hidden = !asset.error; $('asset-message').textContent = asset.error || '';
}
async function resetCamera() {
  if (!viewer) return;
  const model = viewer;
  model.cameraOrbit = '30deg 68deg auto'; model.cameraTarget = 'auto auto auto';
  model.fieldOfView = 'auto';
  await model.updateComplete;
  if (model === viewer) model.jumpCameraToGoal();
}
function play() {
  if (!viewer || changingClip) return;
  // This bundled viewer applies timeScale to both the clip and mixer at play().
  // Activate clips at 1×, then change only the mixer to the requested speed.
  viewer.timeScale = 1;
  if (viewer.currentTime >= viewer.duration - 0.001) viewer.currentTime = 0;
  viewer.play({repetitions: $('loop').checked ? Infinity : 1});
  viewer.timeScale = Number($('speed').value); updateTimeline();
}
function seek(seconds) {
  if (!viewer || changingClip) return;
  viewer.timeScale = 1;
  // Re-enable a completed one-shot action before moving to a new pose.
  viewer.play({repetitions: $('loop').checked ? Infinity : 1}); viewer.pause();
  viewer.currentTime = seconds;
  viewer.timeScale = Number($('speed').value); updateTimeline();
}
async function selectClip(resume = false) {
  const model = viewer, generation = ++clipGeneration;
  changingClip = true; model.pause(); model.timeScale = 1; model.animationName = $('clip').value;
  // This bundled viewer applies animation-name asynchronously. Awaiting prevents
  // its default loop policy from overwriting play({repetitions: 1}).
  await model.updateComplete;
  if (model !== viewer || generation !== clipGeneration) return;
  model.currentTime = 0;
  const policy = active.animations.find(clip => clip.name === $('clip').value)?.loop;
  $('loop').checked = policy === true;
  $('policy').textContent = policy == null ? 'No loop metadata · defaults to one shot; Loop overrides this.' :
    policy ? 'Metadata: looping clip. Loop can be overridden.' : 'Metadata: one-shot clip. Loop can be overridden.';
  model.timeScale = Number($('speed').value);
  changingClip = false; if (resume) play(); updateTimeline();
}
function updateTimeline() {
  if (!viewer) return;
  const duration = Number.isFinite(viewer.duration) ? viewer.duration : 0;
  const time = Number.isFinite(viewer.currentTime) ? viewer.currentTime : 0;
  $('timeline').max = duration || 1; $('timeline').value = Math.min(time, duration);
  $('time').textContent = `${time.toFixed(2)} / ${duration.toFixed(2)} s`;
  $('play').textContent = viewer.paused ? 'Play' : 'Pause';
}
function loadModel(asset) {
  viewer?.pause(); ++clipGeneration; changingClip = false;
  const model = document.createElement('model-viewer'); viewer = model;
  model.id = 'viewer'; model.setAttribute('camera-controls', '');
  model.setAttribute('touch-action', 'pan-y'); model.setAttribute('environment-image', 'neutral');
  model.setAttribute('shadow-intensity', '1'); model.setAttribute('exposure', '1.05');
  model.setAttribute('animation-crossfade-duration', '0'); model.setAttribute('reveal', 'auto');
  model.setAttribute('alt', `Interactive ${asset.title}`);
  $('viewer-host').replaceChildren(model); resetCamera();
  $('animations').disabled = true; $('animations').hidden = true; $('clip').replaceChildren(); $('retry').hidden = true;
  $('load-status').className = ''; $('load-status').textContent = 'Loading 3D model…';
  $('policy').textContent = '';
  $('animation-note').textContent = ''; $('time').textContent = '0.00 / 0.00 s'; $('timeline').value = 0;
  model.addEventListener('load', async () => {
    if (viewer !== model) return;
    await resetCamera();
    if (viewer !== model) return;
    $('load-status').textContent = 'Drag to orbit · scroll or pinch to zoom';
    // The actual loaded GLB is the authority for playable clips.
    const clips = model.availableAnimations;
    $('clip').replaceChildren(...clips.map(name => {const option = text('option', name); option.value = name; return option;}));
    $('animations').disabled = clips.length === 0;
    $('animations').hidden = clips.length === 0;
    $('animation-note').textContent = clips.length ? '' : 'This model has no animation clips.';
    model.timeScale = Number($('speed').value);
    if (clips.length) await selectClip();
  });
  model.addEventListener('error', () => {
    if (viewer !== model) return;
    $('load-status').className = 'warning'; $('load-status').textContent = 'Model could not load. Check the export or retry; available previews and downloads are shown alongside.';
    $('animations').disabled = true; $('animations').hidden = true; $('retry').hidden = false;
  });
  for (const event of ['play', 'pause', 'finished']) model.addEventListener(event, updateTimeline);
  model.src = fileURL(asset.model);
}
function syncDetail() {
  if (!state.asset) {
    viewer?.pause(); viewer = null; active = null; $('viewer-host').replaceChildren();
    if ($('detail').open) $('detail').close(); return;
  }
  const asset = catalog.assets.find(asset => asset.id === state.asset);
  if (!$('detail').open) $('detail').showModal();
  if (!asset) {
    viewer?.pause(); viewer = null; active = null; $('viewer-host').replaceChildren();
    $('asset-title').textContent = 'Asset unavailable'; $('asset-category').textContent = state.asset;
    $('asset-message').textContent = 'This export is missing or was removed. Restore it and the catalog will refresh automatically.';
    $('asset-message').hidden = false; $('animations').disabled = true; $('animations').hidden = true;
    $('clip').replaceChildren(); $('policy').textContent = ''; $('retry').hidden = true;
    $('time').textContent = '0.00 / 0.00 s'; $('timeline').value = 0;
    $('stats').replaceChildren(); $('links').replaceChildren();
    $('preview').replaceChildren(); $('reference').replaceChildren();
    $('load-status').className = ''; $('load-status').textContent = 'Export unavailable'; $('animation-note').textContent = '';
    return;
  }
  const reload = !active || asset.model.version !== active.model.version || asset.id !== active.id;
  const policyChanged = active && JSON.stringify(asset.animations) !== JSON.stringify(active.animations);
  if (JSON.stringify(asset) !== JSON.stringify(active)) renderMetadata(asset);
  active = asset;
  if (reload) loadModel(asset);
  else if (policyChanged && viewer?.loaded && viewer.availableAnimations.length) selectClip(!viewer.paused);
}
async function refresh() {
  if (polling) return; polling = true;
  try {
    const response = await fetch(catalogURL, {cache: 'no-store'});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const next = await response.json();
    if (next.revision !== catalog?.revision) {
      catalog = next;
      const categories = [...new Set(catalog.assets.map(asset => asset.category))].sort();
      if (state.category && !categories.includes(state.category)) categories.push(state.category);
      $('category').replaceChildren(text('option', 'All categories'), ...categories.map(category => {
        const option = text('option', category.replaceAll('_', ' ')); option.value = category; return option;
      })); $('category').firstChild.value = '';
      applyFilters(); renderGrid(); syncDetail();
      $('warnings').textContent = catalog.warnings.join('\n'); $('warnings').hidden = !catalog.warnings.length;
    }
    $('sync').textContent = staticSite ? 'Published catalog · checking for updates' : 'Watching local exports';
  } catch (error) { $('sync').textContent = `Refresh unavailable (${error.message}); retrying…`; }
  finally { polling = false; }
}
$('filters').onsubmit = event => event.preventDefault();
for (const [id, key, event] of [['search', 'q', 'input'], ['category', 'category', 'change'], ['animated', 'animated', 'change']]) {
  $(id).addEventListener(event, () => {state[key] = id === 'animated' ? $(id).checked : $(id).value; writeURL(); if (catalog) renderGrid();});
}
$('refresh').onclick = refresh;
$('close').onclick = () => {state.asset = ''; writeURL(); syncDetail();};
$('detail').addEventListener('cancel', event => {event.preventDefault(); $('close').click();});
$('clip').onchange = () => selectClip(!viewer.paused);
$('play').onclick = () => {if (viewer.paused) play(); else viewer.pause();};
$('speed').onchange = () => {if (viewer) viewer.timeScale = Number($('speed').value);};
$('loop').onchange = () => {if (viewer && !viewer.paused) play();};
$('timeline').oninput = () => seek(Number($('timeline').value));
$('reset-camera').onclick = resetCamera;
for (const [id, factor] of [['zoom-in', 0.8], ['zoom-out', 1.25]]) $(id).onclick = async () => {
  if (!viewer?.loaded) return;
  const model = viewer, orbit = model.getCameraOrbit();
  model.cameraOrbit = `${orbit.theta}rad ${orbit.phi}rad ${orbit.radius * factor}m`;
  await model.updateComplete;
  if (model === viewer) model.jumpCameraToGoal();
};
$('retry').onclick = () => {if (active) loadModel(active);};
window.addEventListener('popstate', () => {
  const p = new URLSearchParams(location.search);
  Object.assign(state, {q: p.get('q') || '', category: p.get('category') || '', animated: p.get('animated') === '1', asset: p.get('asset') || ''});
  applyFilters(); if (catalog) {renderGrid(); syncDetail();}
});
function tick() {if (viewer?.loaded && $('detail').open && !changingClip) updateTimeline(); requestAnimationFrame(tick);}
if (staticSite) {
  $('refresh').textContent = 'Check for updates';
  document.querySelector('header .eyebrow').textContent = 'Odot · Asset library';
}
applyFilters(); refresh(); setInterval(refresh, staticSite ? 60000 : 2000); requestAnimationFrame(tick);
