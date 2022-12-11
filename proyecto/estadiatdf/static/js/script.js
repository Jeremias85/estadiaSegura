$(document).ready( function () {
    $('#paginated').DataTable( {
        "language": {
            "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Spanish.json"
        },
        "pageLength" : 5,
        "lengthMenu": [5, 10, 25, 50]
    } );
    $('#paginated2').DataTable( {
        "language": {
            "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Spanish.json"
        },
        "pageLength" : 5,
        "lengthMenu": [5, 10, 25, 50]
    } );
    $('#paginated3').DataTable( {
        "language": {
            "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Spanish.json"
        },
        "pageLength" : 10,
        "lengthMenu": [10, 25, 50, 100]
    } );

} );
