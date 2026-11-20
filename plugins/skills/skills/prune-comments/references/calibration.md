# Calibration: right and wrong KEEPs

Real comments from a PHP repo, with the verdict and the reason. `@param`, `@return` and `@throws` tags stay in every case: static analysis reads them.

## Right KEEPs

Each one names the mistake an agent would make without it.

```php
/**
 * The helper can refuse before it reads the request. A long request does not fit in the pipe buffer, so the
 * runner cannot write all of it, and the run would fail with `helper_unavailable` in place of the refusal. Thus
 * `cat` reads and discards the remaining request after the helper exits. The request is bounded and the runner
 * closes standard input after it, so `cat` stops.
 */
private function command(string $mode): string
```

Without it, an agent would delete the `cat` as useless.

```php
/**
 * Append an event. Idempotent per (runId, event): a second append for the same pair is ignored, so a
 * replay never enqueues a duplicate.
 */
public function append(string $runId, string $event, array $payload): void;
```

Without it, an agent would write an implementation that enqueues duplicates on replay.

```php
/** The app rejects health pushes carrying more stanza snapshots than this wholesale. */
private const int MAX_STANZA_SNAPSHOTS_PER_PUSH = 500;
```

Without it, an agent would raise the limit here without changing the app that enforces it.

```php
/**
 * A restart_request.changed event for the same service. Defined here rather than borrowed from
 * ServiceEventIngestTest so this file can run on its own.
 */
function restartRequestChangedEvent(Service $service): array
```

Without it, an agent would merge the two copies.

## Wrong KEEPs

```php
/** Primary key of one durable work item. */
final readonly class WorkId

/** Durable provenance that an adoption has landed for this service. */
public function hasAdoptionProvenance(): bool

/**
 * Extracts field from arrow function: fn($model) => $model->field = ...
 */
private function extractFieldsFromArrowFunction(array $params, Expr $expr, array &$fields, Class_ $classNode): void
```

DELETE: each summary restates the name. No mistake can be named.

```php
/**
 * An unrestricted equality is a valid value-object comparison only when both sides are routing enums. An enum
 * compared with a mixed or another non-routing value can hide an engine or kind branch.
 */
private function routingEnumsComparedWithAnUnknownValue(array $leftEnums, array $rightEnums): array
```

DELETE: a *why* stated elsewhere. The name says what it returns, the body shows the rule, the class docblock gives the why for the whole rule, and tests pin the enum-vs-mixed case.

```php
/**
 * True when the route is supported. Missing security evidence is the refusal UnknownSecurityEvidence. A refusal
 * is logged at warning level with $refusalMessage, the instruction ID and the reason, and with the Docker failure
 * and its cause when the evidence is missing. Other failures, for example a programming Error, are not refusals.
 */
public function supports(Cancellation $cancellation, string $instructionId, string $refusalMessage): bool
```

Shorten to `Missing security evidence is the refusal UnknownSecurityEvidence.` Without that sentence, an agent would treat missing evidence as a failure. The other sentences narrate the code.
