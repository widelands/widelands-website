function autoResizeTextarea() {
    const textarea = document.getElementById('id_body');
    textarea.style.height = 'auto'; // Höhe zurücksetzen
    textarea.style.height = textarea.scrollHeight + 'px'; // Höhe an den Inhalt anpassen
}
// Automatische Anpassung beim Laden der Seite
window.onload = autoResizeTextarea;
