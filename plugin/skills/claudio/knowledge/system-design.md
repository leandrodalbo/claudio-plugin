# System design

## Read this when

- several services, nodes or databases are involved
- something must scale, stay up, or be fast under load
- caching, queues, events or a gateway come up
- choosing SQL or NoSQL, or splitting a database

## CAP

A distributed system can't give consistency, availability and partition tolerance all at once.
Networks do partition, so the real choice is: during a partition, favour **consistency** (CP) or
**availability** (AP).

## Distributed systems basics

- **Distributed system:** independent nodes working together over a network.
- **Scalability:** handle more demand without losing performance. **Horizontal** = more nodes;
  **vertical** = a bigger machine.
- **Reliability:** keeps working when parts fail. **Redundancy** removes single points of
  failure; **replication** copies data across nodes.
- **Availability:** the share of time the system is up. Reliable implies available, not the other
  way round.
- **Latency** = response time; **throughput** = work per second.
- **Idempotency:** running an operation twice gives the same result. Make retried operations
  idempotent (ids, upserts).

## Consistency

- **Strong:** every read sees the latest write.
- **Eventual:** replicas catch up later; reads can be stale for a while.
- **Causal:** related operations are seen in the same order by everyone.

## Monolith vs microservices

- **Monolith:** one repository, one deploy. Simple to build, test and run; coupled, scales as one.
- **Microservices:** independent services, scaled and deployed alone, any technology; cost:
  network latency, more moving parts, harder testing and tracing.
- Start simple (KISS); split when a part really needs to scale or change on its own.

## Load balancing

Spreads traffic over replicas of a service; removes a single point of failure.

- Algorithms: round robin, weighted round robin, least connections, least response time.
- Failover: **active-passive** (a standby takes over on health-check failure) or **active-active**
  (all serve, the rest absorb a failed node's load).

## Caching

Keep frequently used data in fast, small storage.

- **CDN:** caches static content close to users.
- Writes: **write-through** (cache + store together; consistent, slower), **write-around** (store
  only; cache filled on the next read), **write-back** (cache first, store later; fast, can lose
  data).
- Invalidation: **TTL** (expires; may serve stale data until then) or **explicit** (the write
  purges the entry; tighter, couples writes to the cache).
- Eviction: LRU, LFU, FIFO, LIFO.
- Cache only what is read often and changes rarely; always know how stale is acceptable.

## Scaling the database

- **Sharding (horizontal partitioning):** rows split across machines. By **range** (simple, range
  queries stay local, risk of hot shards), **hash** (even spread; resharding moves almost
  everything, use consistent hashing), or **list** (known groups: region, tenant).
- **Vertical partitioning:** columns split (hot profile data apart from rarely read metadata).
- Cost of sharding: queries across shards are combined by hand, no joins or foreign keys across
  shards.
- **Replication:** one primary takes writes, replicas serve reads; on failure a replica is
  promoted. **Synchronous** (consistent, slower writes) vs **asynchronous** (fast, replicas may
  lag, a crash can lose a write).
- **Indexes:** usually B-trees, O(log n) lookups for `WHERE`, `JOIN`, `ORDER BY`; cost: slower
  writes and extra storage. Index what you filter and join on.

## SQL vs NoSQL

- **SQL:** fixed schema, rows and columns, ACID transactions. Use when the shape is known and
  correctness matters.
- **NoSQL:** key-value (Redis), document, wide-column; flexible schema, easier horizontal scale,
  weaker guarantees. Use for huge volumes or shapes that vary.

## Messaging

- **Pub/sub** (Kafka): producers publish to a topic, every subscriber gets each message; messages
  are kept, consumers read at their own pace. No atomicity across messages; delivery is usually
  at-least-once, so consumers must handle duplicates (idempotency).
- **Message queue** (RabbitMQ): each message goes to exactly one consumer; consumers compete,
  spreading the load.
- **Event-driven architecture:** services talk through events, not direct calls; the producer
  doesn't know the consumers.
- **Reactive / non-blocking:** treat data as a stream; few threads serve many connections;
  backpressure lets the consumer control the pace.

## Entry points

- **API gateway:** one entry in front of many *different* services; the place for cross-cutting
  concerns once: authentication, rate limiting, logging, routing.
- **Load balancer:** spreads traffic over many *replicas of one* service.
- **Proxy:** forward (in front of clients, hides them) or reverse (in front of servers: hides
  them, can terminate TLS, cache, compress).

## Security

- **Authentication:** who the user is. **Authorization:** what they may do.
- An authorization server issues tokens so each service doesn't build its own login.
