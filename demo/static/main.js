/* globals Chart:false, feather:false */

(function () {
  'use strict'

    htmx.onLoad((e) => {
        const toastElements = document.querySelectorAll('.toast:not(.hide)');
        [...toastElements].map(
            toastEl => {
                var t = new bootstrap.Toast(toastEl, {autohide: false})
                t.show()
                // we should delete the toast from the DOM when its dismissed, instead of just hiding it like Bootstrap wants.
                return t
            }
          );
    })
})()
