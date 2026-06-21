package nakarenta.recipes;

import java.util.HashMap;
import java.util.Map;

public class Recipes {
    private static final String API_URL = "https://api.dofusdb.fr/recipes/";

    private static Recipes instance = null;
    private Map<Integer, Recipe> recipesMap = null;

    private Recipes() {
        recipesMap = new HashMap<>();
    }

    private static Recipes getInstance() {
        if (instance == null) {
            instance = new Recipes();
        }
        return instance;
    }


    public static int addRecipe(Recipe recipe) {
        return getInstance().add(recipe);
    }


    private int add(Recipe recipe) {
        recipesMap.put(recipe.getId(), recipe);
        return recipe.getId();
    }


    public static int generateRecipeWithId(int idApi) {
        Recipes recipes = getInstance();

        // A finir
    }
}
