function SendForm(InputId){
  var formGroup = $('#'+InputId)[0]
  var fData = new FormData(formGroup.id)
  for (var i = 0; i < formGroup.children.length; i++) {
    fData.append(formGroup.children[i])
  }
var request = new XMLHttpRequest();
request.open("POST", formGroup.attributes.action);
request.send(fData);
}
