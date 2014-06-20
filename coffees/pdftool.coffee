console.log 'Starting app'

jQuery.event.props.push 'dataTransfer'
files_array = []
pages_array = []

$(document).ready ->
  if window.File and window.FileReader and window.FileList and window.Blob

    handleRemove = () ->
      $("#sortable").on 'click', ".fa-minus-square", () ->
        if confirm("Are you sure ?")
          $(@).parent().remove()
          updatePagesPosition()

    updatePagesPosition = () ->
      pages_array = []
      for element, i in $('#sortable li')
        pages_array.push(
          filename: $(element).data('filename')
          page: $(element).data('pagenum')
          rotation: $(element).data('rotation') || 0
        )

    handleRotation = () ->
      $('#sortable').on 'click', '.fa-undo', () ->
        rotation = $(@).parent().data('rotation') || 0
        rotation -= 90
        $(@).parent().data 'rotation', rotation
        $(@).siblings('img').css
          "-webkit-transform": "rotate(#{rotation}deg)"
          "-moz-transform": "rotate(#{rotation}deg)"
          "-ms-transform": "rotate(#{rotation}deg)"
          "transform": "rotate(#{rotation}deg)"
        updatePagesPosition()

      $('#sortable').on 'click', '.fa-repeat', () ->
        rotation = $(@).parent().data('rotation') || 0
        rotation += 90
        $(@).parent().data 'rotation', rotation
        $(@).siblings('img').css
          "-webkit-transform": "rotate(#{rotation}deg)"
          "-moz-transform": "rotate(#{rotation}deg)"
          "-ms-transform": "rotate(#{rotation}deg)"
          "transform": "rotate(#{rotation}deg)"
        updatePagesPosition()

    # It works
    handleFileSelect = (evt) ->
      evt.stopPropagation()
      evt.preventDefault()
      files = evt.dataTransfer.files
      $('#drop').remove()

      $('#sortable').sortable
        placeholder: 'ui-sortable-placeholder'
        start: (e, ui) ->
          $(@).attr 'data-previndex', ui.item.index()
        update: (e, ui) ->
          # newIndex = ui.item.index()
          # oldIndex = $(@).attr 'data-previndex'
          # [files_array[oldIndex], files_array[newIndex]] = [
          #   files_array[newIndex], files_array[oldIndex]]
          # $(@).removeAttr 'data-previndex'
          updatePagesPosition()

      data = new FormData()
      data.append('file', files[0])
      filename = files[0].name
      $.ajax
        url: $("#upload-button").data 'preview-url'
        type: 'POST'
        cache: false
        processData: false
        contentType: false
        data: data
        success: (data, textStatus, errors) ->
          for index, bytes of data
            byteCharacters = atob(bytes)
            byteNumbers = new Array(byteCharacters.length)
            for el, i in byteNumbers
              byteNumbers[i] = byteCharacters.charCodeAt(i)
            byteArray = new Uint8Array(byteNumbers)
            blob = new Blob([byteArray], {type: 'application/pdf'})
            url = window.URL.createObjectURL(blob)
            $('#files ul').append "<li class='pdf_thumbnail'
              data-filename='#{filename}' data-pagenum='#{index}'>" +
              "<img src='#{url}' />" +
              '<i class="fa fa-minus-square"></i>' +
              '<i class="fa fa-undo"></i>' +
              '<i class="fa fa-repeat"></i>' +
              '</li>'
          updatePagesPosition()
      files_array.push(files)


    handleDragOver = (evt) ->
      evt.stopPropagation()
      evt.preventDefault()
      evt.dataTransfer.dropEffect = 'copy'

    startUpload = (evt) ->
      evt.stopPropagation()
      evt.preventDefault()
      data = new FormData()
      for el, i in files_array
        data.append('files[]', el[0])
      for el, i in pages_array
        data.append("pages[#{i}]['filename']", el.filename)
        data.append("pages[#{i}]['pagenum']", el.page)
        data.append("pages[#{i}]['rotation']", el.rotation)
      $.ajax
        url: $(@).data 'url'
        type: 'POST'
        cache: false
        processData: false
        contentType: false
        data: data
        beforeSend: () ->
          $('#url').hide()
          $('#loading').show()
        success: (data, textStatus, errors) ->
          byteCharacters = atob(data)
          byteNumbers = new Array(byteCharacters.length)
          for el, i in byteNumbers
            byteNumbers[i] = byteCharacters.charCodeAt(i)
          byteArray = new Uint8Array(byteNumbers)
          blob = new Blob([byteArray], {type: 'application/pdf'})
          url = window.URL.createObjectURL(blob)
          $("#url").attr 'href', url
          $("#url").show()
          $('#loading').hide()
  else
    alert('Your browser is outdated. Please consider upgrading to a newer one.')

  $('#files').bind 'dragover', handleDragOver
  $('#files').bind 'drop', handleFileSelect
  $('#upload-button').bind 'click', startUpload
  handleRemove()
  handleRotation()
