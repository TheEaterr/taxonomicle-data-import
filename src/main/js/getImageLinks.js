import { processString, jsonData, readJSONFile } from './utils.js';
import fs from 'fs';

if (jsonData) {
    const images = readJSONFile('../../../results/images.json')
    let count = 0;
    for (const key in jsonData) {
        const data = jsonData[key];
        const id = processString(key);
        let responseData;
        try {
            if (data.image && !images[id]) {
                const image = encodeURIComponent(data.image);
                const response = await fetch(`https://commons.wikimedia.org/w/api.php?action=query&iiprop=url&prop=imageinfo&titles=File%3A${image}&format=json`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                responseData = await response.json();
                images[id] = responseData.query.pages[Object.keys(responseData.query.pages)[0]].imageinfo[0].url;
            }
        } catch (error) {
            console.error('Error getting image for taxon: ' + key);
            console.log(responseData)
            console.log(`https://commons.wikimedia.org/w/api.php?action=query&iiprop=url&prop=imageinfo&titles=File%3A${encodeURIComponent(data.image)}&format=json`)
        }
        count++;
        if (count % 1000 === 0) {
            fs.writeFileSync('../../../results/images.json', JSON.stringify(images));
            console.log('Processed ' + count + ' taxons');
        }
    }
    fs.writeFileSync('../../../results/images.json', JSON.stringify(images));
}