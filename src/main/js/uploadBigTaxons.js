import { pb, jsonData, getTaxonFilter } from './utils.js';
import fs from 'fs';

// Uploading probability values for a great random taxon generator
const records = await pb.collection('taxon').getFullList({
    filter: "rank.order >= 30 && parent.rank.order < 30",
    fields:  '*,description:excerpt(1,true)'
});
const bigTaxons = [];
let sum = 0;
for (const record of records) {
    const id = record.id;
    const taxons = await pb.collection('taxon').getList(1, 1, {
        expand: 'rank',
        filter: getTaxonFilter(id),
    })
    const probability_root = 3 * Math.log(1 + taxons.totalItems);
    const probability = probability_root * probability_root
    bigTaxons.push(
        {
            "taxon": id,
            "name": record.scientific,
            "count": taxons.totalItems,
            "probability": probability,
            "raw_probability": probability,
        }
    )
    sum += probability;
}
bigTaxons.sort((a, b) => jsonData[b.taxon.split("_")[0]].height - jsonData[a.taxon.split("_")[0]].height);
let rolling_sum = 0;
for (const taxon of bigTaxons) {
    if (taxon.probability != 0) {
        rolling_sum += taxon.probability / sum * 10000;
        taxon.probability = rolling_sum;
    }
}
bigTaxons[bigTaxons.length - 1].probability = 10000;
pb.autoCancellation(false);
bigTaxons.forEach(async taxon => {
    await pb.collection('random_big_taxon').create(taxon);
})
fs.writeFileSync('../../../results/random_big_taxon.json', JSON.stringify(bigTaxons));
