package nakarenta.equipments;

import java.util.ArrayList;
import java.util.List;

import nakarenta.Jobs;
import nakarenta.NakarentaException;

public class Equipment {
    private int id;
    private int idApi;
    private int idCategory;
    private String name;
    private String job;
    private String imgLink;
    private int level;
    private int idPrice = -1;
    private int idRecipe;
    private List<Integer> idEffects;


    public Equipment(int id, int idApi, int idCategory, String name, String imgLink, int level) throws NakarentaException {
        this.id = id;
        this.idApi = idApi;
        this.idCategory = idCategory;
        this.name = name;
        this.job = Jobs.getJobName(idCategory);
        this.imgLink = imgLink;
        this.level = level;
        this.idEffects = new ArrayList<>();
        System.out.println("Équipement ajouté : " + this.name + " (id=" + this.id + ", catégorie=" + this.idCategory + ", métier=" + this.job + ", niveau=" + this.level + ")");
    }


    public Equipment addIdEffect(int idEffects) {
        this.idEffects.add(idEffects);
        return this;
    }


    public Equipment setIdRecipe(int idRecipe) {
        this.idRecipe = idRecipe;
        return this;
    }


    public int getId() {
        return id;
    }


    public String getName() {
        return name;
    }


    public int effectsCount() {
        return this.idEffects.size();
    }

}
