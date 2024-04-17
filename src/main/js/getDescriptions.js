import { processString, jsonData, readJSONFile } from './utils.js';
import fs from 'fs';

const wikiAPIEndpoint = 'https://en.wikipedia.org/w/api.php';
const wikiParams = 'format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=';
export const getDescriptions = async (
	titles
) => {
	const response = await fetch(wikiAPIEndpoint + '?' + wikiParams + titles.join('|') + '&origin=*');
	const responseJson = await response.json();
	const pages = responseJson.query.pages;
	const redirects = {};
	if (responseJson.query.redirects) {
		responseJson.query.redirects.forEach((element) => {
			redirects[element.from] = element.to;
		});
	}
	const descriptions = {};
	Object.keys(pages).forEach((key) => {
		const page = pages[key];
		descriptions[page.title] = page.extract ?? undefined;
	});
	titles.forEach((title) => {
		if (!descriptions[title] && redirects[title]) {
			descriptions[title] = descriptions[redirects[title]];
		}
	});
	return descriptions;
};

if (jsonData) {
    const descriptions = readJSONFile('../../../results/descriptions.json')
    let count = 0;
    // splice keys in groups of 20
    let keys = Object.keys(jsonData);
    keys = keys.filter((key) => !descriptions[key]);
    const keyGroups = [];
    for (let i = 0; i < keys.length; i += 20) {
        keyGroups.push(keys.slice(i, i + 20));
    }

    for (
        let i = 0;
        i < keyGroups.length;
        i++
    ) {
        const keyGroup = keyGroups[i];
        const site_links = keyGroup.map((key) => jsonData[key].site_link);
        const site_link_hash = {}
        keyGroup.forEach((key) => {
            site_link_hash[jsonData[key].site_link] = key;
        });
        try {
            const response = await getDescriptions(site_links);
            for (const key in response) {
                descriptions[site_link_hash[key]] = response[key];
            }
        } catch (error) {
            console.log(error)
            console.error('Error getting description for taxons: ' + keyGroup);
            console.log(responseData)
        }
        count += 20;
        if (count % 100 === 0) {
            fs.writeFileSync('../../../results/descriptions.json', JSON.stringify(descriptions));
            console.log('Processed ' + count + ' taxons');
        }
    }
    fs.writeFileSync('../../../results/descriptions.json', JSON.stringify(descriptions));
}