package nakarenta;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import nakarenta.equipments.Equipment;
import nakarenta.equipments.Equipments;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.List;


public class Extractor {
    public static final String API_URL = "https://api.dofusdb.fr/items";

    private static final int EXCLUDED_TYPE_ID = 203;


    private final HttpClient httpClient = HttpClient.newHttpClient();
    private final Gson gson = new Gson();


    private List<Integer> jobCategories;
    private int minLevel;
    private int maxLevel;


    public Extractor(List<Integer> jobCategories, int minLevel, int maxLevel) {
        this.jobCategories = jobCategories;
        this.minLevel = minLevel;
        this.maxLevel = maxLevel;
    }


    public void extract() throws NakarentaException {
        System.out.println();
        System.out.println("Extraction des équipements pour les catégories de métiers : " + jobCategories);
        System.out.println("Niveau minimum : " + minLevel);
        System.out.println("Niveau maximum : " + maxLevel);

        for (int category : jobCategories) {
            extractCategory(category);
        }
    }


    public void extractCategory(int category) throws NakarentaException {        
        int skip = 0;
        int limit;
        int total;
        JsonObject page;
        JsonArray data;

        System.out.println();
        System.out.println("Extraction des équipements pour la catégorie de métier : " + category);
        do {
            page = requestEquipmentsData(category, skip);
            total = page.get("total").getAsInt();
            limit = page.get("limit").getAsInt();

            data = page.getAsJsonArray("data");
            for (JsonElement element : data) {
                Equipments.addEquipment(element.getAsJsonObject(), category);
            }

            if (limit <= 0) {
                break;
            }
            skip += limit;
        } while (skip < total);
    }


    public JsonObject requestEquipmentsData(int category, int skip) throws NakarentaException {
        String url = buildItemsUrl(category, skip);
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Accept", "application/json")
                .GET()
                .build();
        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200) {
                throw new NakarentaException("Erreur de l'API DofusDB : code " + response.statusCode());
            }
            return gson.fromJson(response.body(), JsonObject.class);
        } catch (IOException e) {
            throw new NakarentaException("Erreur réseau lors de la requête à l'API DofusDB", e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new NakarentaException("Requête à l'API DofusDB interrompue", e);
        }
    }


    private String buildItemsUrl(int category, int skip) {
        StringBuilder query = new StringBuilder();
        appendParam(query, "typeId[$ne]", EXCLUDED_TYPE_ID);    // exclure ce type d'item
        appendParam(query, "typeId[$in][]", category);
        appendParam(query, "level[$gte]", minLevel);
        appendParam(query, "level[$lte]", maxLevel);
        appendParam(query, "$sort", "-level");           // tri par niveau décroissant
        appendParam(query, "$skip", skip);                     // pagination
        appendParam(query, "lang", "fr");
        return API_URL + "?" + query;
    }


    private static void appendParam(StringBuilder query, String key, Object value) {
        if (!query.isEmpty()) {
            query.append('&');
        }

        query.append(URLEncoder.encode(key, StandardCharsets.UTF_8))
             .append('=')
             .append(URLEncoder.encode(value.toString(), StandardCharsets.UTF_8));
    }

}
