package com.example;

public final class IdGenerator {

    private static final IdGenerator INSTANCE = new IdGenerator();

    private long lastId = 0;

    private IdGenerator() {
    }

    public static IdGenerator getInstance() {
        return INSTANCE;
    }

    public long next() {
        lastId++;
        return lastId;
    }
}
