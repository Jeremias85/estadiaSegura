$(document).ready( function () {
    $('#basic-datatable-lista-completa').DataTable( {
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.13.1/i18n/es-ES.json"
        },
        "pageLength" : 10,
        "lengthMenu": [5, 10, 25, 50]
    } )})