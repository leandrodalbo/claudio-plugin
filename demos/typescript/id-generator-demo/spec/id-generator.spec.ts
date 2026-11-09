import { IdGenerator } from "../src/id-generator.ts";

describe("IdGenerator", () => {
  it("returns the same instance every time", () => {
    const first = IdGenerator.getInstance();
    const second = IdGenerator.getInstance();

    expect(second).toBe(first);
  });

  it("returns a higher number on each call to next", () => {
    const generator = IdGenerator.getInstance();

    const first = generator.next();
    const second = generator.next();

    expect(second).toBeGreaterThan(first);
  });
  
});
