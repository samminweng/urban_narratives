import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.apache.commons.io.FileUtils;
import org.json.CDL;
import org.json.JSONArray;
import org.json.JSONObject;

import entity.EntityParser;
import openie.OpenIEParser;
import phrase.ConstituentParser;

public class NLPParser {
    private static Logger logger = Logger.getLogger(NLPParser.class.getName());

    private static JSONArray[] extractPhrases(JSONArray texts) {
        // Tag phrases
        ConstituentParser constituentParser = new ConstituentParser();
        // For each story parse the constituents for each sentence
        JSONArray[] storyPhrases = new JSONArray[texts.length()];
        for (int i = 0; i < texts.length(); i++) {
            try {
                JSONObject inputObj = texts.getJSONObject(i);
                // Collect all the tagged phrases for the story
                JSONArray taggedPhrases = constituentParser.parse(inputObj);
                storyPhrases[i] = taggedPhrases;
                logger.log(Level.INFO, "[phrase] " + i);
            } catch (Exception ex) {
                System.err.println(ex);
            }
        }
        return storyPhrases;
    }

    private static JSONArray[] extractTriples(JSONArray texts) {
        JSONArray[] storyTriples = new JSONArray[texts.length()];
        // Tag relation triples
        OpenIEParser openIEParser = new OpenIEParser();
        for (int i = 0; i < texts.length(); i++) {
            try {
                JSONObject inputObj = texts.getJSONObject(i);
                // Collect all the tagged phrases for the story
                JSONArray taggedTriples = openIEParser.parse(inputObj);
                storyTriples[i] = taggedTriples;
                logger.log(Level.INFO, "[triple] " + i);
            } catch (Exception ex) {
                System.err.println(ex);
            }
        }
        return storyTriples;
    }

    // Extract the entities and entity links to wikipedia
    private static JSONArray[] extractEntities(JSONArray texts) {
        // Tag relation triples
        EntityParser entityParser = new EntityParser();
        JSONArray[] storyEntities = new JSONArray[texts.length()];
        for (int i = 0; i < texts.length(); i++) {
            try {
                JSONObject inputObj = texts.getJSONObject(i);
                // Collect all the tagged phrases for the story
                JSONArray taggedEntities = entityParser.parse(inputObj);
                storyEntities[i] = taggedEntities;
                logger.log(Level.INFO, "[entities] " + i);
            } catch (Exception ex) {
                System.err.println(ex);
            }
        }
        return storyEntities;
    }


    public static void main(String[] args) throws Exception {
        try {
            String caseName = "shareAnIdea";
            String filename = "texts.json";
            String textStr = new String(Files.readAllBytes(Paths.get("data/" + caseName + "/" + filename)));
            JSONArray texts = new JSONArray(textStr);
            JSONArray[] textPhrases = extractPhrases(texts);
            JSONArray[] textTriples = extractTriples(texts);
            JSONArray[] textEntities = extractEntities(texts);
            // Store phrases and relation triples for each story
            JSONArray textJSONArray = new JSONArray();
            for (int i = 0; i < texts.length(); i++) {
                JSONObject inputObj = texts.getJSONObject(i);
                JSONArray taggedPhrases = textPhrases[i];
                JSONArray taggedTriples = textTriples[i];
                JSONArray taggedEntities = textEntities[i];
                // Create output object
                JSONObject textObj = new JSONObject();
                textObj.put("textId", inputObj.get("id"));
                textObj.put("text", inputObj.get("text"));
                textObj.put("taggedPhrases", taggedPhrases);
                textObj.put("taggedTriples", taggedTriples);
                textObj.put("taggedEntities", taggedEntities);
                textJSONArray.put(textObj);
            }
            // Write story phrases and triples to output json file
            String outFileName = "semantics_StanfordNLP";
            PrintWriter printWriter = new PrintWriter(new FileWriter("data/" + caseName + "/" + outFileName + ".json"));
            printWriter.write(textJSONArray.toString());
            printWriter.close();
            // Write the json array to csv file
            File file = new File("data/" + caseName + "/" + outFileName + ".csv");
            String csv = CDL.toString(textJSONArray);
            FileUtils.writeStringToFile(file, csv);
            System.out.println("Data has been Successfully written to " + file);
        } catch (Exception ex) {
            System.err.println(ex);
        }
    }
}