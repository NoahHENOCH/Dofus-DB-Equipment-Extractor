package nakarenta.effects;

public class Effect {
    private int id;
    private int min;
    private int max;
    private String name;

    public Effect(String name, int min, int max, int id) {
        this.name = name;
        this.min = min;
        this.max = max;
        this.id = id;
    }

    public int getId() {
        return id;
    }

}
