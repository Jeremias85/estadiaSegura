$(document).ready( function () {
    $('#basic-datatable3').DataTable( {
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.13.1/i18n/es-ES.json"
        },
        "pageLength" : 5,
        "lengthMenu": [5, 10, 25, 50]
    } )})