submit.onclick = function () {
  const providerName = document.getElementById("providerName").value;
  const spec = document.getElementById("spec").value;

  const url = `/v1/${providerName}/${spec}`;
  const submitButton = document.getElementById("submit");

  submitButton.value = "Building...";

  window.location.href = url;
  return false;
};
