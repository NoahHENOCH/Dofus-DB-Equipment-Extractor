package nakarenta.effects;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import nakarenta.equipments.Equipment;
import nakarenta.NakarentaException;

public class Effects {
    private static final String EFFECTS_NAME_FILE = "/json/effectsName.json";
    private static final String API_EFFECT_URL = "https://api.dofusdb.fr/effects/";

    private static final Pattern PLACEHOLDER_PATTERN = Pattern.compile("#[1-3]");
    private static final Pattern BRACES_PATTERN = Pattern.compile("\\{[^}]*\\}");
    private static final Pattern TAG_PATTERN = Pattern.compile("<.*> ");
    private static final Pattern DAMAGE_PATTERN = Pattern.compile("Dommages?");
    
    private final HttpClient httpClient = HttpClient.newHttpClient();
    private JsonObject effectsNameJsonObject = null;

    private static Effects instance = null;
    private Map<Integer, Effect> effectsMap = null;
    private int nbEffects = 0;

    private Map<Integer, String> effectCacheNameMap = null;
    private List<Integer> effectNotFoundList = null;


    private Effects() throws NakarentaException {
        effectsMap = new HashMap<>();
        effectCacheNameMap = new HashMap<>();
        effectNotFoundList = new ArrayList<>();
        this.effectsNameJsonObject = loadEffectsNameJson(EFFECTS_NAME_FILE);
    }


    private JsonObject loadEffectsNameJson(String path) throws NakarentaException {
        InputStream input = Effects.class.getResourceAsStream(path);
        if (input == null) {
            throw new NakarentaException("Fichier " + path + " introuvable dans les resources");
        }
        try (Reader reader = new InputStreamReader(input, StandardCharsets.UTF_8)) {
            return new Gson().fromJson(reader, JsonObject.class);
        } catch (IOException exception) {
            throw new NakarentaException("Erreur lors de la lecture du fichier " + path, exception);
        }
    }


    private String requestEffectNameFromAPI(int idEffect) throws NakarentaException {
        String url = API_EFFECT_URL + idEffect;
        HttpRequest request = HttpRequest.newBuilder()
                .uri(java.net.URI.create(url))
                .GET()
                .build();

        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200) {
                throw new NakarentaException("Erreur de l'API DofusDB : code " + response.statusCode());
            }
            return new Gson().fromJson(response.body(), JsonObject.class).get("description").getAsJsonObject().get("fr").getAsString();
        } catch (IOException e) {
            throw new NakarentaException("Erreur réseau lors de la requête à l'API DofusDB", e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new NakarentaException("Requête à l'API DofusDB interrompue", e);
        }

    }


    private static String clearEffectName(String effectName) {
        effectName = PLACEHOLDER_PATTERN.matcher(effectName).replaceAll("");   // supprime #1, #2, #3
        effectName = BRACES_PATTERN.matcher(effectName).replaceAll("");        // supprime {...}
        effectName = TAG_PATTERN.matcher(effectName).replaceAll("");           // supprime "<...> "
        effectName = effectName.replace("}", "");                             // } restantes (chaîne littérale)
        effectName = DAMAGE_PATTERN.matcher(effectName).replaceAll("Dommages"); // "Dommage(s)" -> "Dommages"
        return effectName.strip();
    }


    private String getEffectName(int idEffect) throws NakarentaException {
        if (effectCacheNameMap.containsKey(idEffect)) {
            return effectCacheNameMap.get(idEffect);
        }

        if (effectNotFoundList.contains(idEffect)) {
            throw new NakarentaException("Nom d'effet non trouvé pour l'ID " + idEffect + " (déjà tenté)");
        }

        String effectName = requestEffectNameFromAPI(idEffect);
        String clearedEffectName = clearEffectName(effectName);


        if (!effectsNameJsonObject.has(clearedEffectName)) {
            effectNotFoundList.add(idEffect);
            throw new NakarentaException("Nom d'effet non trouvé pour l'ID " + idEffect + " : " + clearedEffectName);
        }

        effectCacheNameMap.put(idEffect, clearedEffectName);
        return clearedEffectName;
    }


    private static Effects getInstance() throws NakarentaException {
        if (instance == null) {
            instance = new Effects();
        }
        return instance;
    }


    private int addEffect(Effect effect) {
        effectsMap.put(effect.getId(), effect);
        return effect.getId();
    }


    public static void addEffectsToEquipment(Equipment equipment, JsonArray jArray) throws NakarentaException {
        Effects effects = getInstance();

        for (JsonElement element : jArray) {
            JsonObject jObject = element.getAsJsonObject();
            int idEffect = jObject.get("effectId").getAsInt();
            int min = jObject.get("from").getAsInt();
            int max = jObject.get("to").getAsInt();

            
            try {
                String effectName = effects.getEffectName(idEffect);

                if (effectName.equals("Arme de chasse")) {
                    min = 1;
                    max = 1;
                }

                if (max == 0 && min > 0) {
                    max = min;
                }

                if (Math.max(min, max) <= 0) continue;
    
                Effect effect = new Effect(effectName, min, max, effects.nbEffects++);
                effects.addEffect(effect);
                equipment.addIdEffect(effect.getId());                
            } catch (NakarentaException e) {
                System.out.println("Erreur lors de l'ajout de l'effet avec l'ID " + idEffect + " à l'équipement " + equipment.getName() + ": " + e.getMessage());
            }

        }
    }

}
