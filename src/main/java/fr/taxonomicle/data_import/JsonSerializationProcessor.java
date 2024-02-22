/*
* ===== This file was modified compared to the version of the original authors =====
* 
* #%L
* Wikidata Toolkit Examples
* %%
* Copyright (C) 2014 - 2015 Wikidata Toolkit Developers
* %%
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* 
*      http://www.apache.org/licenses/LICENSE-2.0
* 
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
* #L%
*/

package fr.taxonomicle.data_import;

import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream;
import org.wikidata.wdtk.datamodel.helpers.Datamodel;
import org.wikidata.wdtk.datamodel.helpers.DatamodelFilter;
import org.wikidata.wdtk.datamodel.implementation.DataObjectFactoryImpl;
import org.wikidata.wdtk.datamodel.helpers.JsonSerializer;
import org.wikidata.wdtk.datamodel.interfaces.*;
import org.wikidata.wdtk.dumpfiles.EntityTimerProcessor;

/**
 * This example illustrates how to create a JSON serialization of some of the
 * data found in a dump. It uses a {@link DatamodelFilter}to eliminate some of the data.
 * <p>
 * As an example, the program only serializes data for people who were born in
 * Dresden, Germany. This can be changed by modifying the code in
 * {@link #includeDocument(ItemDocument)}.
 *
 * @author Markus Kroetzsch
 *
 */
public class JsonSerializationProcessor extends EntityTimerProcessor {

	static final String OUTPUT_FILE_NAME = "json-serialization-taxon-en.json.gz";

	final JsonSerializer jsonSerializer;

	/**
	 * Object used to make simplified copies of Wikidata documents for
	 * re-serialization in JSON.
	 */
	final DatamodelFilter datamodelFilter;

	/**
	 * Runs the example program.
	 *
	 * @param args
	 * @throws IOException
	 *             if there was a problem in writing the output file
	 */
	public static void main(String[] args) throws IOException {
		ExampleHelpers.configureLogging();
		JsonSerializationProcessor.printDocumentation();

		JsonSerializationProcessor jsonSerializationProcessor = new JsonSerializationProcessor();
		ExampleHelpers.processEntitiesFromWikidataDump(jsonSerializationProcessor);
		jsonSerializationProcessor.close();
	}

	/**
	 * Constructor. Initializes various helper objects we use for the JSON
	 * serialization, and opens the file that we want to write to.
	 *
	 * @throws IOException
	 *             if there is a problem opening the output file
	 */
	public JsonSerializationProcessor() throws IOException {
		super(0);
		//Configuration of the filter
		DocumentDataFilter documentDataFilter = new DocumentDataFilter();
		// Only copy English labels, descriptions, and aliases:
		documentDataFilter.setLanguageFilter(Collections.singleton("en"));

		// Only copy statements of some properties:
		Set<PropertyIdValue> propertyFilter = new HashSet<>();
		propertyFilter.add(Datamodel.makeWikidataPropertyIdValue("P171")); // parent taxon
		propertyFilter.add(Datamodel.makeWikidataPropertyIdValue("P18")); // image
		propertyFilter.add(Datamodel.makeWikidataPropertyIdValue("P225")); // taxon name
		propertyFilter.add(Datamodel.makeWikidataPropertyIdValue("P105")); // taxon rank
		propertyFilter.add(Datamodel.makeWikidataPropertyIdValue("P1843")); // taxon common name
		propertyFilter.add(Datamodel.makeWikidataPropertyIdValue("P141")); // IUCN conversation status
		documentDataFilter.setPropertyFilter(propertyFilter);
		// Do not copy any sitelinks:
		documentDataFilter.setSiteLinkFilter(Collections.singleton("enwiki"));

		// The filter is used to remove some parts from the documents we
		// serialize.
		this.datamodelFilter = new DatamodelFilter(new DataObjectFactoryImpl(), documentDataFilter);

		// The (compressed) file we write to.
		OutputStream outputStream = new GzipCompressorOutputStream(
				new BufferedOutputStream(
						ExampleHelpers
								.openExampleFileOuputStream(OUTPUT_FILE_NAME)));
		this.jsonSerializer = new JsonSerializer(outputStream);

		this.jsonSerializer.open();
	}

	@Override
	public void processItemDocument(ItemDocument itemDocument) {
		super.processItemDocument(itemDocument);
		if (includeDocument(itemDocument)) {
			// to use the documentDataFilter
			this.jsonSerializer.processItemDocument(this.datamodelFilter.filter(itemDocument));
			// this.jsonSerializer.processItemDocument(itemDocument);
		}
	}

	@Override
	public void processPropertyDocument(PropertyDocument propertyDocument) {
		super.processPropertyDocument(propertyDocument);
	}

	/**
	 * Prints some basic documentation about this program.
	 */
	public static void printDocumentation() {
		System.out
				.println("********************************************************************");
		System.out.println("*** Wikidata Toolkit: JsonSerializationProcessor");
		System.out.println("*** ");
		System.out
				.println("*** This program will download and process dumps from Wikidata.");
		System.out
				.println("*** It will filter the data and store the results in a new JSON file.");
		System.out.println("*** See source code for further details.");
		System.out
				.println("********************************************************************");
	}

	/**
	 * Closes the output. Should be called after the JSON serialization was
	 * finished.
	 */
	public void close() {
		super.close();
		System.out.println("Serialized "
				+ this.jsonSerializer.getEntityDocumentCount()
				+ " item documents to JSON file " + OUTPUT_FILE_NAME + ".");
		this.jsonSerializer.close();
	}

	/**
	 * Returns true if the given document should be included in the
	 * serialization.
	 *
	 * @param itemDocument
	 *            the document to check
	 * @return true if the document should be serialized
	 */
	private boolean includeDocument(ItemDocument itemDocument) {
		for (StatementGroup sg : itemDocument.getStatementGroups()) {
			// P31 is instance of
			if (!"P31".equals(sg.getProperty().getId())) {
				continue;
			}
			for (Statement s : sg) {
				if (s.getMainSnak() instanceof ValueSnak) {
					Value v = s.getValue();
					if (v instanceof ItemIdValue
							&& "Q16521".equals(((ItemIdValue) v).getId())) {
						return true;
					}
				}
			}
		}
		return false;
	}
}
