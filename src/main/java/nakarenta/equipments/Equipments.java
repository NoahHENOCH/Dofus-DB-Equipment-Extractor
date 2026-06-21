package nakarenta.equipments;

import java.util.HashMap;
import java.util.Map;

import com.google.gson.JsonObject;

import nakarenta.effects.Effects;
import nakarenta.NakarentaException;

public class Equipments {
    private static Equipments instance = null;
    private Map<Integer, Equipment> equipmentsMap = null;

    private Equipments() {
        equipmentsMap = new HashMap<>();
    }


    private static Equipments getInstance() {
        if (instance == null) {
            instance = new Equipments();
        }
        return instance;
    }


    private int addEquipment(Equipment equipment) {
        equipmentsMap.put(equipment.getId(), equipment);
        return equipment.getId();
    }


    public static void addEquipment(JsonObject jObject, int idCategory) throws NakarentaException {
        Equipments equipments = getInstance();

        boolean hasRecipe = jObject.get("hasRecipe").getAsBoolean();
        boolean secretRecipe = jObject.get("secretRecipe").getAsBoolean();
        boolean isLegendary = jObject.get("isLegendary").getAsBoolean();

        if (!hasRecipe || secretRecipe || isLegendary) {
            return;
        }

        String name = jObject.get("name").getAsJsonObject().get("fr").getAsString();
        String imgLink = jObject.get("img").getAsString();
        int level = jObject.get("level").getAsInt();
        int idApi = jObject.get("id").getAsInt();
        int weight = jObject.get("realWeight").getAsInt();

        Equipment equipment = new Equipment(idApi, idCategory, name, imgLink, level, weight);

        Effects.addEffectsToEquipment(equipment, jObject.get("effects").getAsJsonArray());

        if (equipment.effectsCount() == 0) {
            return;
        }

        // Faire un addrecipetoequipment

        equipments.addEquipment(equipment);
    }

}
