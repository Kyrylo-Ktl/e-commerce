$('#deleteCategoryModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget)
    var recipient = button.data('whatever')
    var modal = $(this)
    modal.find('.modal-footer .form-group #category_id').val(recipient)
})
