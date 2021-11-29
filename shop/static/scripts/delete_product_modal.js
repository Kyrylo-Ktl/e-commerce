$('#deleteProductModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget)
    var recipient = button.data('whatever')
    var modal = $(this)
    modal.find('.modal-footer .form-group #delete_product-product_id').val(recipient)
})
