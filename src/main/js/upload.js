import { processString, jsonData, pb, readJSONFile } from './utils.js';

// Gotten froom the python code, as to manually be added here
const TAXON_RANKS = {
    "kindgom": 10,
    "subkingdom": 11,
    "infrakingdom": 12,
    "superphylum": 19,
    "phylum": 20,
    "subphylum": 21,
    "infraphylum": 22,
    "superclass": 29,
    "class": 30,
    "subclass": 31,
    "infraclass": 32,
    "superorder": 39,
    "order": 40,
    "suborder": 41,
    "infraorder": 42,
    "pavorder": 43,
    "superfamily": 49,
    "family": 50,
    "subfamily": 51,
    "tribe": 60,
    "subtribe": 61,
    "genus": 70,
    "subgenus": 71,
    "species": 80,
    "subspecies": 81,
}

const RANK_IDS = {};

for (const key in TAXON_RANKS) {
    const order = TAXON_RANKS[key];
    try {
        const rankEntry = await pb.collection('rank').create({
            "name": key,
            "order": order,
        });
        RANK_IDS[key] = rankEntry.id;
    }
    catch (error) {
        console.error('Error creating taxon_rank: ' + key);
        throw error;
    }
}

if (jsonData) {
    const images = readJSONFile('../../../results/images.json')
    for (const key in jsonData) {
        const data = jsonData[key];
        const id = processString(key);
        const path = data.path.map((pathItem) => processString(pathItem));
        const dbData = {
            "id": id,
            "site_link": data.site_link,
            "rank": RANK_IDS[data.rank],
            "vernacular": data.vernacular ?? undefined,
            "scientific": data.scientific ?? undefined,
            "iucn": data.iucn ?? undefined,
            "image_path": data.image_path ?? false,
            "parent": data.parent ? processString(data.parent) : undefined,
            "path": path,
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
