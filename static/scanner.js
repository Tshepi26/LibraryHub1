/* Camera scanner for book barcodes (EAN-13 ISBN) and QR codes.
   setupScanner({button, reader, input, status, form, autoSubmit, next, isbnOnly}) */
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
  var scanner = null, running = false;
  var START_LABEL = btn.textContent;

  function say(msg, bad) { status.textContent = msg; status.style.color = bad ? '#dc2626' : '#64748b'; }

  async function stop() {
    if (scanner && running) { try { await scanner.stop(); scanner.clear(); } catch (e) {} }
    running = false; scanner = null; btn.textContent = START_LABEL;
  }

  async function begin(facing) {
    var F = Html5QrcodeSupportedFormats;
    scanner = new Html5Qrcode(opts.reader, {
      formatsToSupport: [F.EAN_13, F.QR_CODE],
      experimentalFeatures: { useBarCodeDetectorIfSupported: true },
      verbose: false
    });
    await scanner.start({ facingMode: facing }, { fps: 10, qrbox: { width: 320, height: 200 } },
      function (text) {
        var code = cleanBookCode(text, opts.isbnOnly);
        if (!code) { say('That code is not a book barcode (' + text.slice(0, 20) + '). Keep scanning.', true); return; }
        input.value = code; input.classList.add('scanned');
        say('Scanned ' + code + '.');
        stop();
        if (opts.autoSubmit && opts.form) { document.getElementById(opts.form).submit(); }
        else { var next = document.getElementById(opts.next || ''); if (next) next.focus(); }
      }, function () {});
  }

  btn.addEventListener('click', async function () {
    if (running) { await stop(); say(''); return; }
    if (typeof Html5Qrcode === 'undefined') { say('The scanner library did not load. Check your internet connection.', true); return; }
    if (!window.isSecureContext) { say('The camera only works on https:// or http://localhost.', true); return; }
    try { await begin('environment'); }
    catch (e1) {
      try { await stop(); await begin('user'); }
      catch (e2) { await stop(); say('Could not start the camera. Allow camera access in the browser, then try again.', true); return; }
    }
    running = true; btn.textContent = '⏹ Stop camera';
    say('Hold the back cover about 20 cm from the camera so the barcode fills the box.');
  });
}
