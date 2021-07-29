package openie;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import edu.stanford.nlp.ling.IndexedWord;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations;
import edu.stanford.nlp.semgraph.SemanticGraphEdge;
import edu.stanford.nlp.trees.Constituent;
import edu.stanford.nlp.trees.LabeledScoredConstituentFactory;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeCoreAnnotations;
import org.json.JSONArray;
import org.json.JSONObject;

import edu.stanford.nlp.ie.util.RelationTriple;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.naturalli.NaturalLogicAnnotations;
import edu.stanford.nlp.util.CoreMap;


public class OpenIEParser {
    StanfordCoreNLP pipeline;
    List<String> verbs = Arrays.asList(new String[]{"believe", "think", "mean"});
    List<String> phraseTypes = Arrays.asList(new String[]{"S", "FRAG", "SBAR", "VP"});

    public OpenIEParser() {
        // set up pipeline properties
        Properties props = new Properties();
        // set the list of annotators to run OpenIE
        props.setProperty("annotators", "tokenize,ssplit,pos,lemma,parse,natlog,openie");

        pipeline = new StanfordCoreNLP(props);
    }

    // Capitalise the 1st letter
    private String capitalise(String str) {
        return str.substring(0, 1).toUpperCase() + str.substring(1);
    }

    // Extract the clause from the sentence
    private List<CoreLabel> extractClause(CoreMap sentence, IndexedWord source, int padding) {
        List<CoreLabel> clauseTokens = new ArrayList<CoreLabel>();
        try {
            Tree parseTree = sentence.get(TreeCoreAnnotations.TreeAnnotation.class);
            List<CoreLabel> tokens = sentence.get(CoreAnnotations.TokensAnnotation.class);
            // Collect the constituents for the sentence
            Set<Constituent> constituents = parseTree.constituents(new LabeledScoredConstituentFactory());
            // Collect a list of clauses followed by the source verb
            List<Constituent> clauses = constituents.stream().filter(c -> c.label() != null
                    && phraseTypes.contains(c.label().toString()) && (c.start() == source.index() + padding))
                    .collect(Collectors.toList());

            if (clauses.size() > 0) {
                // Sort phrases by length
                clauses.sort((a, b) -> {
                    // Sort the phrases by length
                    int aLength = a.end() - a.start();
                    int bLength = b.end() - b.start();
                    if (aLength == bLength) {
                        // Sort by the phrase label
                        String aLabel = a.label().toString();
                        String bLabel = b.label().toString();
                        return aLabel.compareTo(bLabel);
                    }
                    return aLength - bLength;
                });
                // The first phrase is the target phrase
                Constituent clause = clauses.get(0);
                // Collect all the tokens of the phrase
                for (int i = 0; i < tokens.size(); i++) {
                    CoreLabel token = tokens.get(i);
                    int tokenId = i + 1;
                    if (tokenId > clause.start() && tokenId <= (clause.end() + 1)) {
                        clauseTokens.add(token);
                    }
                }
            }

        } catch (Exception ex) {
            throw new RuntimeException(ex.getMessage());
        }


        return clauseTokens;

    }

    //
//	// Collect a list of phrases after the source Id
    private Collection<RelationTriple> collectRelationTriplesFromClause(CoreMap sentence, IndexedWord source,
                                                                        int padding) {
        try {
            // Collect the constituents for the sentence
            List<CoreLabel> clauseTokens = extractClause(sentence, source, padding);
            if (clauseTokens.size() > 0) {
                // Collect the tokens as the text
                String clauseText = capitalise(
                        clauseTokens.stream().map(t -> t.word()).collect(Collectors.joining(" ")) + ".");
//					System.out.println("Clause:" + clauseText);
                // Analyze the clause text
                Annotation clauseDoc = new Annotation(clauseText);
                pipeline.annotate(clauseDoc);
                List<CoreMap> clauseSentences = clauseDoc.get(CoreAnnotations.SentencesAnnotation.class);
                if (clauseSentences.size() > 0) {
                    Collection<RelationTriple> clauseTriples = clauseSentences.get(0)
                            .get(NaturalLogicAnnotations.RelationTriplesAnnotation.class);
                    return clauseTriples;
                }
            }
        } catch (Exception e) {
            throw new RuntimeException("Eorror:" + e.getMessage());
        }
        return null;
    }

    int MAXPADDING = 2;

    /**
     * If the sentence matches the pattern "I think + clause" "I believe", then
     * extract triples from the clause. Otherwise, extract triples from the
     * sentence.
     *
     * @param sentence
     */
    private List<JSONObject> extractTriplesFromClause(int sentId, CoreMap sentence) {
        List<JSONObject> jsonTriples = new ArrayList<JSONObject>();// A list of json triples for the sentence
        try {

            // dependency parse for the sentence using enhanced ++
            SemanticGraph dependencyParse = sentence.get(SemanticGraphCoreAnnotations.EnhancedPlusPlusDependenciesAnnotation.class);
            // Get all the edges
            List<SemanticGraphEdge> edges = dependencyParse.edgeListSorted();
            // Collect all the nsubj dependencies
            List<SemanticGraphEdge> nsubjEdges = edges.stream()
                    .filter(edge -> edge.getRelation().getShortName().equals("nsubj")).collect(Collectors.toList());
            // Sort by the source id
            nsubjEdges.sort((a, b) -> a.getSource().index() - b.getSource().index());
            // Go through each edge in the dependency tree
            for (int i = 0; i < nsubjEdges.size(); i++) {
                SemanticGraphEdge edge = nsubjEdges.get(i);
                String dep = edge.getRelation().getShortName();
                IndexedWord source = edge.getSource();
                IndexedWord target = edge.getTarget();
                String sourcePOS = source.get(CoreAnnotations.PartOfSpeechAnnotation.class);
                String targetPOS = target.get(CoreAnnotations.PartOfSpeechAnnotation.class);
                // Check if the source of nsubj (main verb) is either believe or think
                if (sourcePOS.startsWith("VB") && verbs.contains(source.lemma().toLowerCase())
                        && targetPOS.startsWith("PRP")) {
                    int padding = 0;
//                    while (padding < MAXPADDING) {
                    Collection<RelationTriple> relationTriples = this.collectRelationTriplesFromClause(sentence, source, padding);
//                        if (relationTriples != null) {
//                            break;// Found triples, so stop the search.
//                        }
//                        padding++;
//                    }

                    if (relationTriples == null) {
                        // Match the pattern "I think/believe"
                        System.err.println("Sentence:" + sentence.get(CoreAnnotations.TextAnnotation.class));
                        System.err.println("Dep:" + dep + "\tSouce: " + source + "\tTarget: " + target);
                        System.err.println("Can not find triples from the clause");
                    } else {
//						System.out.println("Sentence:" + sentence.get(CoreAnnotations.TextAnnotation.class));
                        for (RelationTriple relationTriple : relationTriples) {
//                            if (relationTriple.confidence == 1) {
//								System.out.println(relationTriple);
                            NLPTriple nlpTriple = new NLPTriple(sentId, relationTriple, source.index() + padding);
                            jsonTriples.add(nlpTriple.getJSONTriple());
//                            }
                        }
                    }
                }
            } // End of loop
        } catch (Exception ex) {
            throw new RuntimeException("Error" + ex.getMessage());
        }
        return jsonTriples;

    }


    private List<JSONObject> extractTriples(int sentId, CoreMap sentence) {
        List<JSONObject> jsonTriples = new ArrayList<JSONObject>();// A list of json triples for the sentence
        try {
            // Get sentence triples for the sentence instead
            Collection<RelationTriple> relationTriples = sentence.get(NaturalLogicAnnotations.RelationTriplesAnnotation.class);
            if (relationTriples.size() > 0) {
                // Create the JSON triple for each relation triple
                for (RelationTriple relationTriple : relationTriples) {
                    NLPTriple nlpTriple = new NLPTriple(sentId, relationTriple, 0);
                    jsonTriples.add(nlpTriple.getJSONTriple());
                }
            } else {
                jsonTriples = extractTriplesFromClause(sentId, sentence);
            }
        } catch (Exception ex) {
            throw new RuntimeException("Error" + ex.getMessage());
        }
        return jsonTriples;
    }

    // Parse the story and extract OpenIE relation
    public JSONArray parse(JSONObject jsonObj) {
        JSONArray taggedTriples = new JSONArray();
        try {
            String story = jsonObj.getString("text");
            Annotation document = new Annotation(story);
            pipeline.annotate(document);
            // System.out.println("\n\n");
            List<CoreMap> sentences = document.get(CoreAnnotations.SentencesAnnotation.class);
            for (int sentId = 0; sentId < sentences.size(); sentId++) {
                CoreMap sentence = sentences.get(sentId);
                // Get sentence triples for the sentence (clause)
                List<JSONObject> triples = extractTriples(sentId, sentence);
                // Print the triple
                for (JSONObject triple : triples) {
                    taggedTriples.put(triple);
                }
            }
        } catch (Exception ex) {
            throw new RuntimeException(ex.getMessage());
        }

        return taggedTriples;
    }

}
