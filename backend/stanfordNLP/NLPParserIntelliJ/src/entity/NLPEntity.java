package entity;

import java.util.List;
import java.util.Map;

import org.json.JSONObject;

import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.util.CoreMap;

public class NLPEntity {
	JSONObject jsonEnitity;

	// Create an JSON entity 
	public NLPEntity(int sentId, CoreMap entityMention) {
		jsonEnitity = createEntity(sentId, entityMention);
	}
	// Get JSON object
	public JSONObject getJSON() {
		return jsonEnitity;
	}

	// Create an entity
	private JSONObject createEntity(int sentId, CoreMap entityMention) {
		try {
			// Get wiki entry link
			String wikiLink = entityMention.get(CoreAnnotations.WikipediaEntityAnnotation.class);
			String text = entityMention.get(CoreAnnotations.TextAnnotation.class);
			String ner = entityMention.get(CoreAnnotations.NamedEntityTagAnnotation.class);
			Map<String, Double> prob = entityMention.get(CoreAnnotations.NamedEntityTagProbsAnnotation.class);
			List<CoreLabel> tokens = entityMention.get(CoreAnnotations.TokensAnnotation.class);
			int[] tokenIds = new int[tokens.size()];
			int i = 0;
			for(CoreLabel token: tokens) {
				tokenIds[i] = token.index();
				i++;
			}
			// Create constituent object to store the starting/end position of phrase-
			JSONObject taggedEntity = new JSONObject();
			taggedEntity.put("sentId", sentId);
			taggedEntity.put("wordIds", tokenIds);
			taggedEntity.put("text", text);
			taggedEntity.put("ner", ner);
			taggedEntity.put("prob", prob);
			taggedEntity.put("wiki", wikiLink);
			return taggedEntity;
		}catch(Exception ex) {
			throw new RuntimeException("Error:"+ ex.getMessage());
		}

	}

}
