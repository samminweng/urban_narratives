package phrase;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.Set;

import org.json.JSONArray;
import org.json.JSONObject;

import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.trees.Constituent;
import edu.stanford.nlp.trees.LabeledScoredConstituentFactory;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeCoreAnnotations;
import edu.stanford.nlp.util.CoreMap;

public class ConstituentParser {
	// public static String text = "I don't think we should have any big shopping
	// malls in the CBD. "
	// + "Shopping malls in other cities usually strip the streets of shops.";
	StanfordCoreNLP pipeline;

	public ConstituentParser() {
		// set up pipeline properties
		Properties props = new Properties();
		props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner,parse");
		// use faster shift reduce parser
		props.setProperty("parse.model", "edu/stanford/nlp/models/srparser/englishSR.ser.gz");
		props.setProperty("parse.maxlen", "100");
		// set the list of annotators to run
		pipeline = new StanfordCoreNLP(props);
	}

	private String getPTB(Constituent constituent) {
		String label = constituent.label().toString();
		int start = constituent.start() + 1;
		int end = constituent.end() + 1;
		return label + "(" + start + "," + end + ")";
	}

	private JSONObject createPhrase(int sentId, Constituent constituent) {
		int start = constituent.start();
		int end = constituent.end();
		String ptb = getPTB(constituent);
		// Create constituent object to store the starting/end position of phrase-
		JSONObject taggedPhrase = new JSONObject();
		taggedPhrase.put("sentId", sentId);
		taggedPhrase.put("ptb", ptb);// Penn Treebank (PTB)
		taggedPhrase.put("start", start + 1);
		taggedPhrase.put("end", end + 1);
		taggedPhrase.put("isLeaf", false);// Default value for the 'isLeaf' property (true: the node is a leaf)
		return taggedPhrase;
	}

	// Check if the noun phrases is the end leaf/does not contain the noun phrase
	private JSONObject checkLeafConstituent(Constituent targetConstituent, Set<Constituent> constituents,
			JSONObject taggedPhrase) {
		boolean isLeaf = true;
		List<String> children = new ArrayList<String>();
		// The only case of the nested constituent
		if (targetConstituent.start() != targetConstituent.end()) {
			for (Constituent constituent : constituents) {
				// Detect if target contains any other constituent,
				// Update 'isLeaf' property to be 'false'
				if (!constituent.equals(targetConstituent) && targetConstituent.contains(constituent)) {
					if (constituent.label().toString().startsWith("NP")) {
						isLeaf = false;
						children.add(getPTB(constituent));
					}
				}
			}
		}
		// For all the other case the node is a leaf
		taggedPhrase.put("isLeaf", isLeaf);
		taggedPhrase.put("leaves", children);
		return taggedPhrase;
	}

	private List<Constituent> sortConstituents(Set<Constituent> constituents) {
		List<Constituent> list = new ArrayList<Constituent>(constituents);
		// Sort the json objects
		list.sort((a, b) -> {
			if (a.label() != null && b.label() != null) {
				String aPTB = a.label().toString();
				String bPTB = b.label().toString();
				// Sort by ptb
				if (aPTB.equals(bPTB)) {
					// Sort by the start and end position
					if (a.start() == b.start()) {
						return a.end() - b.end();
					}
					return a.start() - b.start();
				}
				return aPTB.compareTo(bPTB);
			}
			if (a.label() != null) {
				return 1;
			}
			if (b.label() != null) {
				return -1;
			}
			return 0;
		});
		return list;
	}
	
//	// Print the phrases of a sentence
//	private void printSentence(int sentId, CoreMap sentence, JSONArray sentencePhrases) {
//		// Get the text
//		String text = sentence.get(CoreAnnotations.TextAnnotation.class);
//		System.out.println(text);
//		// Get the token
//		List<CoreLabel> tokens = sentence.get(CoreAnnotations.TokensAnnotation.class);
//		System.out.print("Tokens:");
//		for (CoreLabel token : tokens) {
//			System.out.print(" " + token);
//		}
//		System.out.print("\n");
//		System.out.println(sentencePhrases);
//		System.out.println("Number of phrases of a sentence = "+sentencePhrases.length());
//	}
	// Parse the story and extract the phrases
	public JSONArray parse(JSONObject jsonObj) {
		String story = jsonObj.getString("text");
		Annotation annotation = new Annotation(story);
		pipeline.annotate(annotation);
		// System.out.println("\n\n");
		JSONArray taggedPhrases = new JSONArray();
		List<CoreMap> sentences = annotation.get(CoreAnnotations.SentencesAnnotation.class);
		for (int sentId = 0; sentId < sentences.size(); sentId++) {
			CoreMap sentence = sentences.get(sentId);
			// Get tree annotation for the sentence
			Tree parseTree = sentence.get(TreeCoreAnnotations.TreeAnnotation.class);
			// Collect the constituents for each sentence
			Set<Constituent> constituents = parseTree.constituents(new LabeledScoredConstituentFactory());
			List<Constituent> sortedConstituents = sortConstituents(constituents);
			for (Constituent constituent : sortedConstituents) {
				if (constituent.label() != null) {
					JSONObject taggedPhrase = createPhrase(sentId, constituent);
					// Check if the constituent has any nested constituent
					if (constituent.label().toString().equals("NP")) {
						taggedPhrase = checkLeafConstituent(constituent, constituents, taggedPhrase);
//						System.out.println("found constituent: " + taggedPhrase);
					}
					taggedPhrases.put(taggedPhrase);
				}
			}
		}
		return taggedPhrases;
	}

}
