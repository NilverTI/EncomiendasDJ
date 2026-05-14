// Cierre automático de alertas después de 5 segundos
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.fadeAlert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Confirmación reutilizable para acciones críticas
function confirmarAccion(mensaje) {
    return confirm(mensaje || '¿Estás seguro de realizar esta acción?');
}

// Filas clickeables en tablas (si tienen data-href)
document.addEventListener('DOMContentLoaded', function () {
    const rows = document.querySelectorAll('tr[data-href]');
    rows.forEach(function (row) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function () {
            window.location.href = row.getAttribute('data-href');
        });
    });
});
