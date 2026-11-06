/* Camera scanner for book barcodes (EAN-13 ISBN) and QR codes.
   setupScanner({button, reader, input, status, form, autoSubmit, next, isbnOnly})
   Lists every camera so you can pick the right one, warns about a black picture,
   and can also read a barcode from a photo. */
function isValidIsbn13(d) {
  if (!/^97[89]\d{10}$/.test(d)) return false;
  var sum = 0;
  for (var i = 0; i < 13; i++) sum += parseInt(d[i], 10) * (i % 2 === 0 ? 1 : 3);
  return sum % 10 === 0;
}
function cleanBookCode(text, isbnOnly) {
  var t = text.trim().toUpperCase();
  if (!isbnOnly && /^ACC-\d{4}$/.test(t)) return t;
  var digits = t.replace(/[\s-]/g, '');
  return isValidIsbn13(digits) ? digits : null;
}

function setupScanner(opts) {
  var btn = document.getElementById(opts.button);
  var input = document.getElementById(opts.input);
  var status = document.getElementById(opts.status);
  var scanner = null, running = false, blackTimer = null, cameraSelect = null;
  var START_LABEL = btn.textContent;

  function say(msg, bad) { status.textContent = msg; status.style.color = bad ? '#dc2626' : '#64748b'; }
  function config() {
    var F = Html5QrcodeSupportedFormats;
    return { formatsToSupport: [F.EAN_13, F.QR_CODE],
             experimentalFeatures: { useBarCodeDetectorIfSupported: true }, verbose: false };
  }

  function handle(text) {
    var code = cleanBookCode(text, opts.isbnOnly);
    if (!code) { say('That code is not a book barcode (' + text.slice(0, 20) + '). Keep scanning.', true); return false; }
    input.value = code; input.classList.add('scanned');
    say('Scanned ' + code + '.');
    if (opts.autoSubmit && opts.form) { document.getElementById(opts.form).submit(); }
    else { var next = document.getElementById(opts.next || ''); if (next) next.focus(); }
    return true;
  }

  async function stop() {
    clearTimeout(blackTimer);
    if (scanner && running) { try { await scanner.stop(); scanner.clear(); } catch (e) {} }
    running = false; scanner = null; btn.textContent = START_LABEL;
  }

  async function startWith(cameraId) {
    scanner = new Html5Qrcode(opts.reader, config());
    await scanner.start(cameraId, { fps: 10, qrbox: { width: 320, height: 200 } },
      function (text) { if (handle(text)) { stop(); } }, function () {});
    running = true; btn.textContent = '⏹ Stop camera';
    say('Hold the back cover about 20 cm from the camera so the barcode fills the box.');
    // Black-picture warning: the camera opened but sent no image
    blackTimer = setTimeout(function () {
      var v = document.querySelector('#' + opts.reader + ' video');
      if (!v || !v.videoWidth || v.readyState < 2) {
        say('The camera opened but shows no picture. Choose a different camera from the list, close other apps using the camera, or scan from a photo below.', true);
        if (cameraSelect) cameraSelect.style.display = 'block';
      }
    }, 3500);
  }

  function addExtras() {
    if (cameraSelect) return;
    cameraSelect = document.createElement('select');
    cameraSelect.setAttribute('aria-label', 'Choose camera');
    cameraSelect.style.cssText = 'display:none;margin-top:10px';
    btn.parentNode.insertBefore(cameraSelect, status);
    cameraSelect.addEventListener('change', async function () {
      try { sessionStorage.setItem('libraryCamera', cameraSelect.value); } catch (e) {}
      await stop();
      try { await startWith(cameraSelect.value); } catch (e) { say('Could not start that camera. Try another one.', true); }
    });

    var wrap = document.createElement('div');
    wrap.style.cssText = 'margin-top:10px';
    wrap.innerHTML = '<label style="font-size:12px;color:#64748b;font-weight:500">No camera picture? Scan from a photo instead:</label>';
    var file = document.createElement('input');
    file.type = 'file'; file.accept = 'image/*'; file.style.marginTop = '4px';
    wrap.appendChild(file);
    status.parentNode.insertBefore(wrap, status.nextSibling);
    file.addEventListener('change', async function () {
      if (!file.files || !file.files[0]) return;
      var tmp = new Html5Qrcode(opts.reader, config());
      try { var text = await tmp.scanFile(file.files[0], false); handle(text); }
      catch (e) { say('No barcode found in that photo. Use a sharp, close-up photo with the whole barcode in view.', true); }
      try { tmp.clear(); } catch (e) {}
      file.value = '';
    });
  }

  function pickDefault(cams) {
    var saved = null;
    try { saved = sessionStorage.getItem('libraryCamera'); } catch (e) {}
    if (saved && cams.some(function (c) { return c.id === saved; })) return saved;
    var good = cams.filter(function (c) { return !/infrared|\bir\b|virtual|obs|snap|ndi|depth/i.test(c.label || ''); });
    var pool = good.length ? good : cams;
    var back = pool.filter(function (c) { return /back|rear|environment/i.test(c.label || ''); });
    return (back[0] || pool[0]).id;
  }

  btn.addEventListener('click', async function () {
    if (running) { await stop(); say(''); return; }
    if (typeof Html5Qrcode === 'undefined') { say('The scanner library did not load. Check your internet connection.', true); return; }
    if (!window.isSecureContext) { say('The camera only works on https:// or http://localhost.', true); return; }
    addExtras();
    var cams = [];
    try { cams = await Html5Qrcode.getCameras(); }
    catch (e) { say('Camera access is blocked. Click the camera or padlock icon next to the address bar, choose Allow, then press the button again.', true); return; }
    if (!cams.length) { say('No camera was found on this computer. Use the photo option below, or type the ISBN.', true); return; }

    cameraSelect.innerHTML = '';
    cams.forEach(function (c, i) {
      var o = document.createElement('option'); o.value = c.id; o.textContent = c.label || ('Camera ' + (i + 1));
      cameraSelect.appendChild(o);
    });
    var chosen = pickDefault(cams);
    cameraSelect.value = chosen;
    cameraSelect.style.display = cams.length > 1 ? 'block' : 'none';
    try { await startWith(chosen); }
    catch (e) {
      await stop();
      say('Could not start the camera. Another app may be using it, or access was denied. Close other apps using the camera and try again.', true);
    }
  });
}