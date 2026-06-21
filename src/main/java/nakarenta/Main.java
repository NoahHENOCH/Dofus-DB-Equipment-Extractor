package nakarenta;

import java.util.List;
import java.util.Scanner;

public class Main {

    private static int promptLevel(int min, int max, Scanner scanner)
    {
        int level;
        do {
            System.out.print("Entrez un niveau (entre " + min + " et " + max + "): ");
            level = scanner.nextInt();
        } while (level < min || level > max);
        return level;
    }


    private static List<Integer> promptJobCategories(Scanner scanner) throws NakarentaException {
        List<String> jobNames = Jobs.getJobNames();
        int indice;
        int jobIndex;
        String selectedJob;

        System.out.println();
        System.out.println("Veuillez entrer l'indice du métier pour lequel vous souhaitez extraire les équipements :");
        for (indice = 0; indice < jobNames.size(); indice++) {
            System.out.println(indice + " : " + jobNames.get(indice));
        }

        do {
            System.out.print("Entrez un indice de métier (entre 0 et " + (jobNames.size() - 1) + "): ");
            jobIndex = scanner.nextInt();
        } while (jobIndex < 0 || jobIndex >= jobNames.size());

        selectedJob = jobNames.get(jobIndex);
        System.out.println("Vous avez sélectionné le métier : " + selectedJob);

        return Jobs.getCategories(selectedJob);
    }
    

    public static void main(String[] args) {
        System.out.println("Dofus DB Equipment Extractor - démarrage");
        int minLevel;
        int maxLevel;
        List<Integer> selectedJobCategories;
        Scanner scanner = new Scanner(System.in);


        try {
            selectedJobCategories = promptJobCategories(scanner);
            
            System.out.println();
            System.out.println("Veuillez entrer le niveau minimum et maximum pour l'extraction des équipements.");
            System.out.println("Niveau minimum: ");
            minLevel = promptLevel(1, 200, scanner);

            System.out.println();
            System.out.println("Niveau maximum: ");
            maxLevel = promptLevel(minLevel, 200, scanner);

            System.out.println();
            System.out.println("Extraction des équipements du niveau " + minLevel + " au niveau "+ maxLevel + "...");
            
            // Appel de la méthode d'extraction des équipements ici
            Extractor extractor = new Extractor(selectedJobCategories, minLevel, maxLevel);
            extractor.extract();

        } catch (NakarentaException e) {
            System.err.println("Erreur lors du chargement des métiers : " + e.getMessage());
        }
        scanner.close();
        
    }
}
