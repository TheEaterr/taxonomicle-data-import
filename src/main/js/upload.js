import fs from 'fs';
import PocketBase from 'pocketbase';

const pb = new PocketBase('http://127.0.0.1:8090');


// Function to read JSON file synchronously
function readJSONFile(filename) {
    try {
        const data = fs.readFileSync(filename, 'utf8');
        const jsonData = JSON.parse(data);
        return jsonData;
    } catch (error) {
        console.error('Error reading JSON file:', error.message);
        return undefined;
    }
}

function processString(inputString) {
    if (inputString.length > 15) {
        throw new Error('Id ' + inputString + ' is too long (more than 15 characters)');
    } else {
        while (inputString.length < 15) {
            inputString += '_';
        }
        return inputString;
    }
}

// Replace 'example.json' with the path to your JSON file
const jsonFilename = '../../../results/animalia_tree.json';

// Read JSON file
const jsonData = readJSONFile(jsonFilename);

if (jsonData) {
    for (const key in jsonData) {
        const data = jsonData[key];
        const id = processString(key);
        const dbData = {
            "id": id,
            "site_link": data.site_link,
            "rank": data.rank,
            "vernacular": data.vernacular ?? undefined,
            "scientific": data.scientific ?? undefined,
            "image": data.image ?? undefined,
            "iucn": data.iucn ?? undefined,
            "field": data.parent ? processString(data.parent) : undefined
        };
        try {
            await pb.collection('taxon').create(dbData);
        } catch (error) {
            console.error('Error creating taxon: ' + key, error.message);
        }
    }
}
