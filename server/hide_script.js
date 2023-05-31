let elementToSave = null;
let next = null;

function hide() {
  elementToSave = document.getElementById("door_fieldset")
  elementToSave.remove()
}

function show() {
  next = document.getElementById("next")
  next.remove()
  document.getElementById("the_form").appendChild(elementToSave)
  document.getElementById("the_form").appendChild(next)
}
