function loadDBobjects(targetElementID, endpoint, optionsFunc, dataFunction) {
    const objectSelect = document.getElementById(targetElementID);
    const options = objectSelect.options;

    if (optionsFunc) {
        optionsFunc(options);
    }

    fetch(endpoint)
    .then(response => response.json())
    .then(data => dataFunction(data, options))
    .catch(error => {
        console.error('Error loading data:', error);
    });

}

const communeEndpoint = (regionId) => `/api/v1/regions/${regionId}/communes`;

function communeOptionsFunction(options) {
    for (let i = 0; i < options.length; i++) {
        const option = options[i];
        option.disabled = false;
    }
}

function communeDataFunction(data, options) {
    const communes_ids = data.map(commune => String(commune.id));
    for (let i = 1; i < options.length; i++) {
        const option = options[i];
        if (!Array.from(communes_ids).includes(option.value)) option.disabled = true;
    }
}

const regionEndpoint = (communeId) => `/api/v1/communes/${communeId}/region`;

function regionOptionsFunction(options) {
    for (let i = 0; i < options.length; i++) {
        const option = options[i];
        option.selected = false;
    }
}

function regionDataFunction(data, options) {
    for (let i = 0; i < options.length; i++) {
        const option = options[i];
        option.selected = option.value === String(data.id);
    }
}

function loadCommunes(id, targetElementID='commune', optionsFunc=communeOptionsFunction, dataFunction=communeDataFunction) {
    loadDBobjects(targetElementID, communeEndpoint(id), optionsFunc, dataFunction)
}

function loadRegions(id, targetElementID='region', optionsFunc=regionOptionsFunction, dataFunction=regionDataFunction) {
    loadDBobjects(targetElementID, regionEndpoint(id), optionsFunc, dataFunction)
}