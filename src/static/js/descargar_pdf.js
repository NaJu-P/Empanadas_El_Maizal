function generarPDF() {
  const elemento = document.getElementById('ripped-paper');
  const ahora = new Date();
  const fecha = ahora.toLocaleDateString().replace(/\//g, '-');
  const hora = ahora.toLocaleTimeString().replace(/:/g, '-');
  const fecha_exacta = `${fecha}_${hora}`;

  // Convertir px a mm (1px = 0.264583 mm)
  const anchoPx = elemento.scrollWidth;
  const altoPx = elemento.scrollHeight;
  const anchoMm = anchoPx * 0.264583;
  const altoMm = altoPx * 0.264583;

  const opciones = {
    margin: 10,  // 10mm por cada lado
    filename: `comprobante_${fecha_exacta}.pdf`,
    image: { type: 'jpeg', quality: 1 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };

  html2pdf()
    .set(opciones)
    .from(elemento)
    .save()
    .catch(err => {
      console.error("Error al generar el PDF:", err);
    });
}
