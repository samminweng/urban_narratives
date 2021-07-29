package openie;
import java.util.Arrays;
import java.util.List;

import org.json.JSONObject;

import edu.stanford.nlp.ie.util.RelationTriple;
import edu.stanford.nlp.ling.CoreLabel;

public class NLPTriple {

	JSONObject jsonTriple;

	// Get the json triple
	public NLPTriple(int sentId, RelationTriple triple, int padding) {
		jsonTriple = createTriple(sentId, triple, padding);
	}

	public JSONObject getJSONTriple() {
		return jsonTriple;
	}

	// Go through each word and convert each word to an array of Ids (int)
	private int[] convertWordIds(List<CoreLabel> words, int padding) {
		int[] wordIds = new int[words.size()];
		for (int i = 0; i < words.size(); i++) {
			CoreLabel word = words.get(i);
			wordIds[i] = word.index() + padding;
		}
		// Sort wordIds by id
		Arrays.sort(wordIds);

		return wordIds;
	}

	/**
	 * Create the triple object from relation triples.
	 * 
	 * @param sentId
	 * @param triple
	 * @return
	 */
	private JSONObject createTriple(int sentId, RelationTriple triple, int padding) {
		double confidence = triple.confidence;
		List<CoreLabel> subjectWords = triple.subject;
		List<CoreLabel> relationWords = triple.relation;
		List<CoreLabel> objectWords = triple.object;
		// Create constituent object to store the starting/end position of phrase-
		JSONObject taggedTriple = new JSONObject();
		taggedTriple.put("sentId", sentId);
		taggedTriple.put("confidence", confidence);
		taggedTriple.put("subject", convertWordIds(subjectWords, padding));
		taggedTriple.put("subjectWords", triple.subjectLemmaGloss());
		taggedTriple.put("relation", convertWordIds(relationWords, padding));
		taggedTriple.put("relationWords", triple.relationLemmaGloss());
		taggedTriple.put("object", convertWordIds(objectWords, padding));
		taggedTriple.put("objectWords", triple.objectLemmaGloss());
		return taggedTriple;
	}
}
