package nakarenta.ingredients;

import nakarenta.recipes.Recipe;

public class Ingredient {
    private int id;
    private boolean hasRecipe;
    private boolean isEquipment;
    private int idRecipe = -1;


    public int getId() {
        return id;
    }


    public boolean hasRecipe() {
        return hasRecipe;
    }


    public boolean isEquipment() {
        return isEquipment;
    }

    public void setRecipe(int idRecipe) {
        this.idRecipe = idRecipe;
    }

}
