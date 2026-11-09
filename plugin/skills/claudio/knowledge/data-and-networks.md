# Data and networks

## Read this when

- designing tables, relations or queries
- networking, ports, firewalls or addresses come up
- working with processes, the shell, files or Linux itself

## Relational modelling

- **One-to-many:** a teacher teaches many courses; the "many" side holds the foreign key.
- **Many-to-many:** students and courses; needs a junction table (`Enrollment(student_id,
  course_id)`).

## Normalization

Store each fact once, or updates, inserts and deletes go wrong (anomalies).

- **1NF:** one value per column, no lists.
- **2NF:** with a composite key, every column depends on the whole key.
- **3NF:** no column depends on another non-key column.
- Normalized = correct, cheap safe writes, more joins. Denormalized = fast reads, risk of
  inconsistency. Choose on purpose.

## SQL and relational algebra

Selection σ = `WHERE`; projection π = `SELECT` columns; join ⋈ = `JOIN` on a foreign key;
intersection ∩ = `INTERSECT`. Index the columns you filter and join on; check the query plan when
it is slow.

## Networking

- **Protocol:** an agreed format for data over a network.
- **OSI layers:** 7 application (HTTP, SMTP) · 6 presentation (encoding, encryption) · 5 session ·
  4 transport (**TCP**: reliable, ordered, connection; **UDP**: fast, no guarantee) · 3 network
  (IP addresses, routing; IPv4 32 bits, IPv6 128 bits) · 2 data link (MAC) · 1 physical.
- **Firewall:** rules for traffic in and out; allow only what is needed, deny the rest.
- **NAT:** source NAT lets private hosts reach the internet; destination NAT forwards inbound
  traffic to a private host.
- **Subnets:** a mask splits the address into network and host parts; a `/24` leaves 8 bits, 254
  usable hosts (network and broadcast addresses are reserved).

## Operating systems and Linux

- The OS manages CPU, memory, storage and devices. The **kernel** runs privileged; programs run in
  **user space** and ask through **system calls**.
- **Process:** a running program with its own memory. **Thread:** a unit of execution inside a
  process; threads share memory, so shared state needs synchronization.
- **Shell:** reads commands and asks the kernel to run them. **File descriptors:** small numbers
  for open files, sockets, pipes; every process starts with stdin 0, stdout 1, stderr 2.
- **Pipes** (`ps aux | grep java`): one program's stdout into the next one's stdin, nothing on
  disk.
- **IPC:** pipes (one way, related processes), shared memory (fastest, needs synchronization),
  sockets (any processes, across machines), signals (`SIGTERM`, `SIGKILL`).
- `fork()` clones a process; the child inherits the open file descriptors.
