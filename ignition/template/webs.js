function SendForm(){
var inputF = $("#test")[0];
var formData = new FormData(inputF);
var request = new XMLHttpRequest();
formData.append(inputF.name, inputF.value)
var target = $("#id_test")[0];
request.open("POST", target.value);
request.send(formData);
//Zero Out the text Fields
$("#test")[0] = ''
}
