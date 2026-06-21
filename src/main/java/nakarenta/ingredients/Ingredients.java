package nakarenta.ingredients;

import java.util.HashMap;
import java.util.Map;

public class Ingredients {
    private static Ingredients instance = null;
    private Map<Integer, Ingredient> ingredientsMap = null;

    private Ingredients() {
        ingredientsMap = new HashMap<>();
    }

    private static Ingredients getInstance() {
        if (instance == null) {
            instance = new Ingredients();
        }
        return instance;
    }


    public static int addIngredient(Ingredient ingredient) {
        return getInstance().add(ingredient);
    }


    private int add(Ingredient ingredient) {
        ingredientsMap.put(ingredient.getId(), ingredient);
        return ingredient.getId();
    }
}
