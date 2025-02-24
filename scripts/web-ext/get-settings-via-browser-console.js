// Function for loading 'js-yaml' and waiting until it is available.
async function loadYamlLib() {
    return new Promise((resolve, reject) => {
        if (window.jsyaml) {
            resolve();
            return;
        }
        const script = document.createElement("script");
        script.src = "https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js";
        script.onload = () => resolve();
        script.onerror = () => reject(new Error("Failed to load js-yaml from CDN."));
        document.head.appendChild(script);
    });
}

// Function to send a GET request and fetch available presets data.
async function fetchAvailablePresets() {
    const baseUrl = `${window.location.origin}`;
    const url = `${baseUrl}/api/v1/presets`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status} while fetching ${url}.`);
        }
        const responseData = await response.json();
        return responseData.presets;
    } catch (error) {
        console.error("Error fetching available presets:", error);
        return [];
    }
}

// Function to sort presets by the 'caption' field
function sortPresetsByCaption(presets) {
    // The `b.caption.toLowerCase()` call is unnecessary because localeCompare already handles case-insensitive sorting.
    return presets.sort((a, b) => a.caption.localeCompare(b.caption));
}

// Function to find a preset by its caption and return its index + 1
function getPresetNumberByName(presets, caption) {
    const index = presets.findIndex(preset => preset.caption === caption);
    if (index === -1) {
        console.error(`Preset with caption "${caption}" not found.`);
        return null;
    }
    return index + 1;
}

// Format the data in the format that is used in the 'settings.yaml' file.
function formatStateDataAsYaml(stateData) {
    return {
        adjustments: {
            exposure: stateData.exposure ?? 0,
            contrast: stateData.contrast ?? 0,
            temperature: stateData.temperature ?? 0,
            tint: stateData.tint ?? 0,
            color_boost: stateData.color_boost ?? 0,
        },
        effects: {
            grain: stateData.is_grain_enabled ? stateData.grain : "Off",
            bloom: stateData.is_bloom_enabled ? stateData.bloom : "Off",
            halation: stateData.is_halation_enabled ? stateData.halation : "Off",
            vignette: stateData.is_vignette_enabled
                ? {
                      exposure: stateData.vignette_exposure ?? 0,
                      size: stateData.vignette_size ?? 0,
                      feather: stateData.vignette_feather ?? 0,
                  } : "Off",
        },
    };
}

// Format the data in the format that is used in CLI arguments.
function formatStateDataAsCLIArgs(yamlData) {
    return [
        `--set_exposure ${yamlData.adjustments.exposure}`,
        `--set_contrast ${yamlData.adjustments.contrast}`,
        `--set_temperature ${yamlData.adjustments.temperature}`,
        `--set_tint ${yamlData.adjustments.tint}`,
        `--set_color_boost ${yamlData.adjustments.color_boost}`,
        yamlData.effects.grain !== "Off" ? `--set_grain ${yamlData.effects.grain}` : "",
        yamlData.effects.bloom !== "Off" ? `--set_bloom ${yamlData.effects.bloom}` : "",
        yamlData.effects.halation !== "Off" ? `--set_halation ${yamlData.effects.halation}` : "",
        yamlData.effects.vignette !== "Off"
            ? [
                  `--set_vignette_exposure ${yamlData.effects.vignette.exposure}`,
                  `--set_vignette_size ${yamlData.effects.vignette.size}`,
                  `--set_vignette_feather ${yamlData.effects.vignette.feather}`,
              ].join(" ") : "",
    ]
}


// Function to process chosen preset and state data.
async function processPresetAndStateData() {
    await loadYamlLib();

    // Process state data stored in local storage.
    const rawStateData = localStorage.getItem("stateByImageId");
    if (rawStateData) {
        const parsedStateData = JSON.parse(rawStateData);
        const stateData = parsedStateData[Object.keys(parsedStateData)[0]];

        // Format the state data into YAML and CLI arguments
        const formattedDataAsYaml = formatStateDataAsYaml(stateData);
        let formattedDataAsCLIArgs = formatStateDataAsCLIArgs(formattedDataAsYaml);

        // Fetch the list of available presets
        const availablePresets = await fetchAvailablePresets();
        if (availablePresets.length === 0) {
            console.log("No presets available.");
            return;
        }

        // Sort presets and find the selected preset number
        const sortedAvailablePresets = sortPresetsByCaption(availablePresets);
        const presetName = stateData.caption;
        const presetNumber = getPresetNumberByName(sortedAvailablePresets, presetName);
        // Add the preset number to the list of CLI arguments
        const formattedPresetIdAsCLIArg = `--preset ${presetNumber}`;
        formattedDataAsCLIArgs.unshift(formattedPresetIdAsCLIArg);

        // Clear console before print the result.
        console.clear();
        // Print the selected preset.
        console.log(`🎞 Preset: '${presetName}'. Use '${formattedPresetIdAsCLIArg}' as command line argument.`);
        // Print the result state data in YAML format in the console.
        console.log("📝 The settings that can be used in the 'settings.yaml' file are:\n");
        console.log(window.jsyaml.dump(formattedDataAsYaml));
        // Print the result state data in CLI args format in the console.
        console.log("\n📟 Settings that can be used as command line arguments:\n");
        console.log(formattedDataAsCLIArgs.filter(arg => arg !== "").join(" "));
    } else {
        console.log("No data found in localStorage for stateByImageId.");
    }
}

/* Run the main function to get the state data from local storage
and print it to the console in YAML and CLI args formats. */
processPresetAndStateData();