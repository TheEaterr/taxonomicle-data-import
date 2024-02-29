import { processString, jsonData, pb } from './utils.js';

if (jsonData) {
    const images = readJSONFile('../../../results/images.json')
    for (const key in jsonData) {
        const data = jsonData[key];
        const id = processString(key);
        const dbData = {
            "id": id,
            "site_link": data.site_link,
            "rank": data.rank,
            "vernacular": data.vernacular ?? undefined,
            "scientific": data.scientific ?? undefined,
            "iucn": data.iucn ?? undefined,
            "image_path": data.image_path ?? false,
            "parent": data.parent ? processString(data.parent) : undefined
        };
        if (images[id]) {
            dbData.image_link = images[id];
        }
        try {
            await pb.collection('taxon').create(dbData);
        } catch (error) {
            console.error('Error creating taxon: ' + key);
            throw error;
        }
    }
}