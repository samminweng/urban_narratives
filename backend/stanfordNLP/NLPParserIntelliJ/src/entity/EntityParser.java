package entity;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.json.JSONArray;
import org.json.JSONObject;

import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;

public class EntityParser {
	StanfordCoreNLP pipeline;

	public EntityParser() {
		// set up pipeline properties
		Properties props = new Properties();
		// set the list of annotators to run Entity link
//		props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner");
		props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner,entitylink");
		props.setProperty("entitylink.wikidict", "edu/stanford/nlp/models/kbp/english/wikidict.tab.gz");
		props.setProperty("entitylink.caseless", "true");

		pipeline = new StanfordCoreNLP(props);
	}

	/**
	 * Extract the entities of the given sentence
	 * 
	 * @param sentId
	 * @param sentence
	 * @return
	 */
	private List<JSONObject> extractSentenceEntities(int sentId, CoreMap sentence) {
		try {
//			System.out.println("Sentence:" + sentence.get(CoreAnnotations.TextAnnotation.class));
			List<JSONObject> jsonEntities = new ArrayList<JSONObject>();
			// Token level
			List<CoreMap> entityMentions = sentence.get(CoreAnnotations.MentionsAnnotation.class);
			for (CoreMap entityMention : entityMentions) {
				// Get wiki entry link
//				String wikiLink = entityMention.get(CoreAnnotations.WikipediaEntityAnnotation.class);
//				if(wikiLink != null && !wikiLink.equals("")) {// Skip the entity that does not have the link
				NLPEntity nlpEntity = new NLPEntity(sentId, entityMention);
				jsonEntities.add(nlpEntity.getJSON());
//				}
			}
			return jsonEntities;
		} catch (Exception ex) {
			throw new RuntimeException("Error" + ex.getMessage());
		}

	}

	public JSONArray parse(JSONObject jsonObj) {
		String story = jsonObj.getString("text");
		Annotation document = new Annotation(story);
		pipeline.annotate(document);
//		System.out.println("\n\n");
		JSONArray taggedEntities = new JSONArray();
		List<CoreMap> sentences = document.get(CoreAnnotations.SentencesAnnotation.class);
		for (int sentId = 0; sentId < sentences.size(); sentId++) {
			CoreMap sentence = sentences.get(sentId);
			// Get sentence entities for the sentence
			List<JSONObject> entities = extractSentenceEntities(sentId, sentence);
//			// Add the entity
			for (JSONObject entity : entities) {
				taggedEntities.put(entity);
			}
		}
		return taggedEntities;
	}
}
