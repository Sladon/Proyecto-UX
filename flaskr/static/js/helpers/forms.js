function getFormField(classes, labelText, index, name, inputType = 'text', inputClass = 'form-control', onBlurFunc = null, value='') {
    const formField = document.createElement("div");
    formField.classList.add(...classes.split(' '));

    const label = document.createElement("label");
    label.textContent = labelText;
    label.setAttribute("for", `${name}`);

    const input = document.createElement("input");
    input.type = inputType;
    input.classList.add(inputClass);
    input.id = `${name}_${index}`;
    input.name = name;
    input.value = value;

    formField.appendChild(label);
    formField.appendChild(input);

    if (onBlurFunc) {
        input.addEventListener("blur", function(ev) { onBlurFunc(ev.target) }, false)
    }

    return formField;
}

function validateRun(input) {
    const parentDiv = input.parentElement;
    const feedbackElement = parentDiv.querySelector('.invalid-feedback');
    const helpElement = parentDiv.querySelector('.form-text.text-muted');

    fetch(`/api/v1/validate/run/${input.value}`)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
        })
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
        .catch(error => {
            console.error('Error validating run value:', error);
        });
}

function removePerson(button) {
    const selectedPersonDiv = button.parentElement.parentElement;
    const parentDiv = selectedPersonDiv.parentElement;
    const personsContainer = Array.from(parentDiv.children);

    const personIndex = selectedPersonDiv.querySelector('input[name=index]').value;

    if (personsContainer.length === 1) {
        const inputFields = selectedPersonDiv.querySelectorAll('input');
        for (let i = 1; i < inputFields.length; i++) {
            inputFields[i].value = '';
        }
    } else {
        for (let i = 0; i < personsContainer.length; i++) {
            const personDiv = personsContainer[i];
            const personIndexInput = personDiv.querySelector('input[name=index]');
            if (personIndexInput.value > personIndex) personIndexInput.value--;
        }
        selectedPersonDiv.remove();
    }
}

function addSellerBuyerElement(containerClass, rutValue = undefined, shareValue = undefined) {
    const sellerBuyerContainer = document.getElementById(`${containerClass}s`);
    const newSellerBuyerIndx = sellerBuyerContainer.children.length+1;

    const sellerBuyerElement = document.createElement("div");
    sellerBuyerElement.classList.add('form-row', containerClass);

    const rutName = `${containerClass}_rut`
    const shareName = `${containerClass}_share`
    const indexField = getFormField('form-group col-md-1', "N°", newSellerBuyerIndx, "index");
    const indexInputField = indexField.querySelector('input');
    indexInputField.value = newSellerBuyerIndx;
    indexInputField.setAttribute('readonly', '');
    const rutField = getFormField('form-group col-md-6', 'RUN o RUT', newSellerBuyerIndx, rutName, undefined, undefined, validateRun, rutValue);
    const shareField = getFormField('form-group col-md-4', '% de derecho', newSellerBuyerIndx, shareName, 'number', 'form-control', undefined, shareValue);

    const divButtonWrapper = document.createElement("div");
    divButtonWrapper.classList.add('form-group', 'col-md-1');

    const label = document.createElement("label");
    label.textContent = "Quitar"
    label.classList.add("text-white")

    const divButton = document.createElement("div");
    divButton.classList.add('remove', 'btn', 'btn-danger');
    divButton.textContent = 'Quitar';
    divButton.addEventListener("click", function(ev) { removePerson(ev.target) })
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