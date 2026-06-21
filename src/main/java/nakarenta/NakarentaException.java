package nakarenta;

public class NakarentaException extends Exception {
    public NakarentaException(String message) {
        super(message);
    }

    public NakarentaException(String message, Throwable cause) {
        super(message, cause);
    }
}
