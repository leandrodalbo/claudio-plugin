package com.example;

import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class IdGeneratorTest {

    @Test
    void getInstanceAlwaysReturnsTheSameObject() {
        IdGenerator first = IdGenerator.getInstance();
        IdGenerator second = IdGenerator.getInstance();

        assertSame(first, second);
    }

    @Test
    void nextKeepsRisingOnEveryCall() {
        IdGenerator generator = IdGenerator.getInstance();

        long first = generator.next();
        long second = generator.next();
        long third = generator.next();

        assertTrue(first < second && second < third);
    }
}
