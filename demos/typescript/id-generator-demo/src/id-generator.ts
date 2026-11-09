export class IdGenerator {
  private static readonly instance = new IdGenerator();

  private lastId = 0;

  private constructor() {}

  static getInstance(): IdGenerator {
    return IdGenerator.instance;
  }

  next(): number {
    this.lastId += 1;
    return this.lastId;
  }
}
