import { pb, getTaxonFilter } from './utils.js';
import fs from 'fs';

const getRandomParent = (index) => {
	return pb
		.collection('random_big_taxon')
		.getFirstListItem(`${index} < probability`, {
            expand: 'taxon',
			sort: '+probability'
		});
};

const TAXON_FIELDS = 'scientific,description:excerpt(250,true)';
const randomTaxonTest = [];

for (let i = 0; i < 100; i++) {
    const randomParentIndex = (2999 * i) % 10000;
    const parent = await getRandomParent(randomParentIndex);
	const taxon = (
		await pb.collection('taxon').getFirstListItem(getTaxonFilter(parent.taxon), {
			fields: TAXON_FIELDS,
            sort: '@random',
		})
	);

    randomTaxonTest.push({
        parent: parent.expand.taxon.scientific,
        taxon: taxon.scientific,
        description: taxon.description,
    });
}

fs.writeFileSync('../../../results/random_taxon_test.json', JSON.stringify(randomTaxonTest));
