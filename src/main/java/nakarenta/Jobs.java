package nakarenta;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;



public class Jobs {
    private static final String PATH = "/json/jobs.json";
    private static Jobs instance = null;
    private final Map<String, List<Integer>> jobsMap;
    private static final String ALL_JOBS_KEY = "All Jobs";


    private Jobs() throws NakarentaException {
        this.jobsMap = load(PATH);

        ArrayList<Integer> allCategories = new ArrayList<>();
        for (List<Integer> categories : jobsMap.values()) {
            for (Integer category : categories) {
                if (!allCategories.contains(category)) {
                    allCategories.add(category);
                }
            }
        }
        jobsMap.put(ALL_JOBS_KEY, allCategories);
        
        System.out.println(jobsMap.size() + " métiers chargés.");
    }


    public static Jobs getInstance() throws NakarentaException {
        if (instance == null) {
            instance = new Jobs();
        }
        return instance;
    }


    private static Map<String, List<Integer>> load(String path) throws NakarentaException {
        InputStream input = Jobs.class.getResourceAsStream(path);
        if (input == null) {
            throw new NakarentaException("Fichier " + path + " introuvable dans les resources");
        }

        Map<String, List<Integer>> result = new HashMap<>();
        try (Reader reader = new InputStreamReader(input, StandardCharsets.UTF_8)) {
            JsonArray jobs = new Gson().fromJson(reader, JsonArray.class);
            for (JsonElement element : jobs) {
                JsonObject job = element.getAsJsonObject();
                String name = job.get("name").getAsString();

                List<Integer> categories = new ArrayList<>();
                for (JsonElement category : job.getAsJsonArray("category_id")) {
                    categories.add(category.getAsInt());
                }
                result.put(name, categories);
            }
        } catch (IOException e) {
            throw new NakarentaException("Erreur de lecture de " + path, e);
        }
        return result;
    }


    public static List<Integer> getCategories(String name) throws NakarentaException {
        return getInstance().jobsMap.get(name);
    }


    public static Map<String, List<Integer>> getAll() throws NakarentaException {
        return getInstance().jobsMap;
    }


    public static int size() throws NakarentaException {
        return getInstance().jobsMap.size();
    }


    public static List<String> getJobNames() throws NakarentaException {
        return new ArrayList<>(getInstance().jobsMap.keySet());
    }


    public static String getJobName(int categoryId) throws NakarentaException {
        for (Map.Entry<String, List<Integer>> entry : getInstance().jobsMap.entrySet()) {
            if (!entry.getKey().equals(ALL_JOBS_KEY) && entry.getValue().contains(categoryId)) {
                return entry.getKey();
            }
        }
        return null;
    }
}
