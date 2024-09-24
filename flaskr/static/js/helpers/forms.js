function getFormField(classes, labelText, index, name, inputType = 'text', value = '', onBlurFunc = null) {
  const formField = document.createElement("div");
  formField.classList.add(...classes.split(' '));

  const label = document.createElement("label");
  label.classList.add("block", "text-gray-700");
  label.textContent = labelText;
  label.setAttribute("for", `${name}`);

  const input = document.createElement("input");
  input.type = inputType;
  input.classList.add("form-control", "w-full", "border", "rounded", "p-2");
  input.id = `${name}_${index}`;
  input.name = name;
  input.value = value;

  formField.appendChild(label);
  formField.appendChild(input);

  if (onBlurFunc) {
      input.addEventListener("blur", function(ev) { onBlurFunc(ev.target); }, false);
  }

  return formField;
}

function validateRun(input) {
  const parentDiv = input.parentElement;
  let feedbackElement = parentDiv.querySelector('.invalid-feedback');
  let helpElement = parentDiv.querySelector('.form-text.text-muted');

  if (!feedbackElement) {
      feedbackElement = document.createElement("div");
      feedbackElement.classList.add("invalid-feedback");
      parentDiv.appendChild(feedbackElement);
  }

  if (!helpElement) {
      helpElement = document.createElement("small");
      helpElement.classList.add("form-text", "text-muted");
      parentDiv.appendChild(helpElement);
  }

  fetch(`/api/v1/validate/run/${input.value}`)
      .then(response => response.ok ? response.json() : Promise.reject(`Error ${response.status}: ${response.statusText}`))
      .then(data => {
          if (data.status === 'OK') {
              input.classList.remove('is-invalid');
              feedbackElement.textContent = '';
              helpElement.textContent = data.message;
          } else {
              input.classList.add('is-invalid');
              feedbackElement.textContent = data.status;
              helpElement.textContent = data.message;
          }
      })
      .catch(error => console.error('Error validating run value:', error));
}

function removePerson(button) {
  const selectedPersonDiv = button.closest('.form-row');
  if (!selectedPersonDiv) return;
  
  const parentDiv = selectedPersonDiv.parentElement;
  const personsContainer = Array.from(parentDiv.children);

  if (personsContainer.length === 1) {
      const remainingPersonDiv = personsContainer[0];
      remainingPersonDiv.querySelectorAll('input').forEach(input => {
          if (input.name !== "index") input.value = '';
      });
  } else {
      selectedPersonDiv.remove();
      const updatedPersonsContainer = Array.from(parentDiv.children);
      updatedPersonsContainer.forEach((personDiv, index) => {
          const indexInput = personDiv.querySelector('input[name="index"]');
          if (indexInput) {
              indexInput.value = index + 1; // Set the new index
              indexInput.id = `${indexInput.name}_${index + 1}`;
          }

          const rutInput = personDiv.querySelector(`input[name*="_rut"]`);
          if (rutInput) {
              rutInput.id = `${rutInput.name}_${index + 1}`;
          }

          const shareInput = personDiv.querySelector(`input[name*="_share"]`);
          if (shareInput) {
              shareInput.id = `${shareInput.name}_${index + 1}`;
          }
      });
  }
}


function addSellerBuyerElement(containerClass, rutValue = '', shareValue = '') {
  const sellerBuyerContainer = document.getElementById(`${containerClass}s`);
  const newSellerBuyerIndx = sellerBuyerContainer.children.length + 1;

  const sellerBuyerElement = document.createElement("div");
  sellerBuyerElement.classList.add('form-row', containerClass);

  const indexField = getFormField('form-group col-md-1', "N°", newSellerBuyerIndx, "index");
  const indexInputField = indexField.querySelector('input');
  indexInputField.value = newSellerBuyerIndx;
  indexInputField.setAttribute('readonly', '');
  const rutField = getFormField('form-group col-md-6', 'RUN o RUT', newSellerBuyerIndx, `${containerClass}_rut`, 'text', rutValue, validateRun);
  const shareField = getFormField('form-group col-md-4', '% de derecho', newSellerBuyerIndx, `${containerClass}_share`, 'number', shareValue);

  const divButtonWrapper = document.createElement("div");
  divButtonWrapper.classList.add('form-group', 'col-md-1');

  const label = document.createElement("label");
  label.textContent = "Quitar";
  label.classList.add("text-white");

  const divButton = document.createElement("button");
  divButton.classList.add('remove', 'btn', 'btn-danger');
  divButton.textContent = 'Quitar';
  divButton.type = "button";
  divButton.addEventListener("click", function(ev) { removePerson(ev.target); });
  divButtonWrapper.appendChild(label);
  divButtonWrapper.appendChild(divButton);

  const feedback = document.createElement("div");
  feedback.classList.add("invalid-feedback");
  const small = document.createElement("small");
  small.classList.add("form-text", "text-muted");

  sellerBuyerElement.appendChild(indexField);
  sellerBuyerElement.appendChild(rutField);
  sellerBuyerElement.appendChild(shareField);
  sellerBuyerElement.appendChild(divButtonWrapper);
  rutField.appendChild(feedback);
  rutField.appendChild(small);

  sellerBuyerContainer.appendChild(sellerBuyerElement);
}