function updatePorts(comPort, baudRate) {
  document.getElementById("port").innerText = comPort;
  document.getElementById("baud").innerText = baudRate;
}

// Make POST request on form submit
function submitForm() {

  fetch('/pair', {
    method: 'POST'
  })
  .then(response => response.json())
  .then(data => {

    // Update spans
    updatePorts(data.comPort, data.baudRate);

  });

}
