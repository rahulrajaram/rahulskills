---
name: fp-refine
description: "Transform imperative code into functional-programming-first, immutable, DSL-oriented structures optimized for agent-amenability. Diagnoses mutable state machines, long imperative workflows, string dispatch, scattered validation, exception control flow, and deep mutation — then applies declarative refactoring patterns. Use when the user says /fp-refine, 'make this functional', 'refactor to FP', or asks to make code more declarative or agent-friendly."
argument-hint: "[file or module path]"
version: 1.0.0
---

# Skill: Declarative Refinement — FP-First, DSL-Oriented Code Transformation

## Identity and Purpose

You are transforming code to be **functional-programming-first, immutable, and DSL-oriented**, using **agent-amenability as the taste criterion** for which specific patterns to apply.

The governing insight: code that is declarative, data-driven, and composed of pure functions is code that AI agents can reliably read, reason about, and modify. Imperative code with mutable state, interleaved side effects, and irregular control flow defeats agent-driven modification at scale.

---

## Core Commitments

When you examine code, you are looking through three lenses simultaneously:

**FP-first.** Pure functions, immutable data, algebraic data types, composition, typed error handling. Every piece of logic should be a function from input to output with no hidden dependencies.

**Immutability.** Data does not change after creation. New states are new values. History is preserved by construction. The agent never needs to ask "what could have mutated this?"

**DSL-oriented.** Domain logic is expressed as data structures that follow regular schemas. Adding behavior means adding an entry, not modifying control flow. The code reads as a description of the domain, not as instructions to the machine.

**Filtered by agent-amenability.** Not all FP is good. Not all DSLs are good. The specific patterns chosen must make the code *more* amenable to understanding and modification by an agent, not less. Point-free obfuscation, monad transformer stacks, and opaque macro expansions are FP/DSL patterns that fail this filter.

---

## Usage

```
/fp-refine
/fp-refine src/order_processor.py
/fp-refine "the payment workflow module"
```

When invoked:

1. Read the target code (or scan the codebase if no target specified).
2. Run the diagnostic phase to identify imperative anti-patterns.
3. Rank findings by severity.
4. Propose transformations, starting with the highest-impact patterns.
5. Apply transformations with the user's approval.

---

## Diagnostic Phase: What to Look For

Before transforming anything, identify which imperative patterns are present and how severely they resist agent modification.

### Pattern 1: Mutable State Machines

**Symptoms:**
- A class or module with a `state` or `status` field that gets reassigned
- Methods or functions containing `if self.state == "X"` / `switch(this.state)` chains
- State transitions buried inside business logic alongside side effects
- Auxiliary state fields (`retries`, `last_error`, `flags`) that interact with the primary state in non-obvious ways

**Why this resists agents:** The agent must simulate execution to know what state the system is in at any point. Adding a state requires understanding all existing states and their interactions. The transition topology is invisible.

**Severity: Critical.** This is the single most damaging pattern for agent-driven modification of workflow code.

### Pattern 2: Long Imperative Workflows

**Symptoms:**
- A function longer than ~30 lines that performs a sequence of steps
- Intermediate mutable variables that accumulate results
- Side effects (I/O, logging, notifications) interleaved with computation
- Early returns or exception throws for error cases mid-sequence
- Comments like `# Step 1: ...`, `# Step 2: ...` acting as the only structural markers

**Why this resists agents:** The agent cannot modify step N without understanding steps 1 through N-1 because mutable variables create hidden data dependencies. Adding a step requires finding the right insertion point in a sequence where position matters.

**Severity: High.**

### Pattern 3: Branching Dispatch on Strings or Untyped Values

**Symptoms:**
- `if/elif/else` chains or `switch/case` blocks dispatching on string values, integer codes, or similar
- The same dispatch value checked in multiple places across the codebase
- No single location that enumerates all possible values
- Default/else branches that silently swallow unknown cases

**Why this resists agents:** There is no way to know if all cases are handled without searching the entire codebase. Adding a new case means finding every dispatch site. The compiler/type-checker cannot help.

**Severity: High.**

### Pattern 4: Scattered Validation and Business Rules

**Symptoms:**
- Validation checks spread across multiple functions, often duplicated
- Business rules embedded inside controllers, handlers, or I/O code
- Rules that interact in non-obvious ways (order-dependent, mutually exclusive) but are not co-located
- No clear boundary between "validated" and "unvalidated" data

**Why this resists agents:** The agent cannot find all the rules for a given concern. Modifying a rule requires understanding whether the same check exists elsewhere. There is no schema governing what a rule looks like.

**Severity: Medium-High.**

### Pattern 5: Exception-Based Control Flow

**Symptoms:**
- `try/catch` blocks used for expected conditions (not just truly exceptional failures)
- Exceptions carrying business meaning ("InsufficientFundsException", "UserNotVerifiedException")
- Catch blocks that modify state or perform business logic
- Functions where the caller must know which exceptions might be thrown (undocumented)

**Why this resists agents:** Exceptions create invisible control flow paths. The agent cannot see the full set of outcomes from reading a function's signature. Error handling logic is separated from the code that produces errors, sometimes by many stack frames.

**Severity: Medium.**

### Pattern 6: Deep Mutation of Shared Data Structures

**Symptoms:**
- Functions that receive an object and modify it in place
- Multiple functions operating on the same mutable data structure across a request lifecycle
- Defensive copying (`clone()`, `copy.deepcopy()`) as a workaround
- Bugs caused by unexpected aliasing

**Why this resists agents:** The agent cannot reason locally. Any function that has a reference to the data might have changed it. The agent must trace all access paths to understand current state.

**Severity: Medium.**

---

## Transformation Patterns

For each diagnostic pattern, here is the target state and the transformation approach.

### Transform 1: State Machine -> Transition Table

**Target:** A declarative definition that separates the topology of the machine (what states exist, what transitions are allowed) from the behavior at each transition (what computation happens) from the side effects triggered by transitions.

**Structure:**

```
States:       enumerated type, each carrying its own data
Transitions:  data structure mapping (CurrentState, Event) -> (TargetState, Action)
Side effects: data structure mapping (CurrentState, Event) -> [Effect]
Error policy:  data structure mapping State -> ErrorHandling
Executor:     generic runtime that interprets the above definitions
```

**The key insight:** The agent edits the *definition*. The executor is written once and not touched. Adding a state means adding an entry to an enum and entries to the transition/effect tables.

**Language-specific approaches:**

#### Python
```python
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, TypeVar

class OrderStatus(Enum):
    PENDING = auto()
    VALIDATED = auto()
    CHARGED = auto()
    CANCELLED = auto()
    FAILED = auto()

class OrderEvent(Enum):
    VALIDATE = auto()
    CHARGE = auto()
    CANCEL = auto()

@dataclass(frozen=True)
class Transition:
    target: OrderStatus
    action: Callable  # pure function: State -> Result[State, Error]

@dataclass(frozen=True)
class WorkflowDef:
    transitions: dict[tuple[OrderStatus, OrderEvent], Transition]
    effects: dict[tuple[OrderStatus, OrderEvent], list[Callable]]

order_workflow = WorkflowDef(
    transitions={
        (OrderStatus.PENDING, OrderEvent.VALIDATE):
            Transition(OrderStatus.VALIDATED, validate_order),
        (OrderStatus.PENDING, OrderEvent.CANCEL):
            Transition(OrderStatus.CANCELLED, cancel_order),
        (OrderStatus.VALIDATED, OrderEvent.CHARGE):
            Transition(OrderStatus.CHARGED, charge_order),
    },
    effects={
        (OrderStatus.PENDING, OrderEvent.CANCEL): [notify_customer_cancelled],
        (OrderStatus.VALIDATED, OrderEvent.CHARGE): [send_receipt, update_inventory],
    },
)
```

#### Common Lisp
```lisp
(defmacro defworkflow (name &body states)
  "Define a state machine as a transition table."
  `(defparameter ,name
     (make-workflow
       :transitions
       (list
         ,@(loop for (state . transitions) in states
                 append (loop for (event arrow target . rest) in transitions
                              collect `(make-transition
                                        :from ,state
                                        :event ,event
                                        :to ,target
                                        :action ,(getf rest :action)
                                        :effects (list ,@(getf rest :effects)))))))))

(defworkflow *order-workflow*
  (:pending
    (:validate -> :validated
     :action #'validate-order)
    (:cancel -> :cancelled
     :action #'cancel-order
     :effects (#'notify-customer-cancelled)))
  (:validated
    (:charge -> :charged
     :action #'charge-order
     :effects (#'send-receipt #'update-inventory))))
```

#### Java
```java
public sealed interface OrderState permits Pending, Validated, Charged, Cancelled {
    record Pending(Order order) implements OrderState {}
    record Validated(Order order, ValidationResult result) implements OrderState {}
    record Charged(Order order, Payment payment) implements OrderState {}
    record Cancelled(Order order, String reason) implements OrderState {}
}

public enum OrderEvent { VALIDATE, CHARGE, CANCEL }

// Transition table as data
Map<Pair<Class<? extends OrderState>, OrderEvent>, TransitionDef<?, ?>> transitions = Map.of(
    Pair.of(Pending.class, OrderEvent.VALIDATE),
        TransitionDef.of(OrderActions::validateOrder),
    Pair.of(Pending.class, OrderEvent.CANCEL),
        TransitionDef.of(OrderActions::cancelOrder),
    Pair.of(Validated.class, OrderEvent.CHARGE),
        TransitionDef.of(OrderActions::chargeOrder)
);
```

#### Rust
```rust
#[derive(Debug, Clone)]
enum OrderState {
    Pending { order: Order },
    Validated { order: Order, result: ValidationResult },
    Charged { order: Order, payment: Payment },
    Cancelled { order: Order, reason: String },
    Failed { order: Order, error: WorkflowError },
}

#[derive(Debug, Clone, Hash, Eq, PartialEq)]
enum OrderEvent {
    Validate,
    Charge,
    Cancel,
}

// Each transition is a pure function
fn apply_transition(state: OrderState, event: OrderEvent) -> Result<OrderState, WorkflowError> {
    match (state, event) {
        (OrderState::Pending { order }, OrderEvent::Validate) =>
            validate_order(order).map(|(order, result)|
                OrderState::Validated { order, result }),
        (OrderState::Pending { order }, OrderEvent::Cancel) =>
            Ok(OrderState::Cancelled { order, reason: "user_requested".into() }),
        (OrderState::Validated { order, .. }, OrderEvent::Charge) =>
            charge_order(order).map(|(order, payment)|
                OrderState::Charged { order, payment }),
        (state, event) =>
            Err(WorkflowError::InvalidTransition { state, event }),
    }
}
```

#### TypeScript
```typescript
type OrderState =
    | { kind: 'pending'; order: Order }
    | { kind: 'validated'; order: Order; result: ValidationResult }
    | { kind: 'charged'; order: Order; payment: Payment }
    | { kind: 'cancelled'; order: Order; reason: string }

type OrderEvent = 'validate' | 'charge' | 'cancel'

type TransitionDef = {
    target: OrderState['kind']
    action: (state: OrderState) => Result<OrderState, WorkflowError>
    effects?: readonly SideEffect[]
}

const transitions: Record<string, Record<string, TransitionDef>> = {
    pending: {
        validate: {
            target: 'validated',
            action: validateOrder,
            effects: [],
        },
        cancel: {
            target: 'cancelled',
            action: cancelOrder,
            effects: [notifyCustomerCancelled],
        },
    },
    validated: {
        charge: {
            target: 'charged',
            action: chargeOrder,
            effects: [sendReceipt, updateInventory],
        },
    },
} as const
```

---

### Transform 2: Imperative Workflow -> Typed Pipeline

**Target:** A sequence of named, typed, pure transformation stages. Each stage has a clear input type and output type. The pipeline definition is separate from stage implementations.

**Structure:**

```
Stage:     named pure function, InputType -> Result[OutputType, Error]
Pipeline:  ordered list of stages, where each stage's output type matches the next stage's input type
Executor:  generic runtime that threads data through the pipeline, handling errors uniformly
```

**Language-specific approaches:**

#### Python
```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable
from result import Result, Ok, Err  # or your own Result type

@dataclass(frozen=True)
class Stage(Generic[I, O]):
    name: str
    execute: Callable[[I], Result[O, PipelineError]]

@dataclass(frozen=True)
class Pipeline:
    stages: tuple[Stage, ...]

    def run(self, initial_input):
        current = Ok(initial_input)
        for stage in self.stages:
            match current:
                case Ok(value):
                    current = stage.execute(value)
                case Err(_):
                    break
        return current

order_pipeline = Pipeline(stages=(
    Stage("validate",   validate_order),
    Stage("price",      calculate_pricing),
    Stage("check_fraud", fraud_check),
    Stage("charge",     process_payment),
    Stage("fulfill",    initiate_fulfillment),
))
```

#### Common Lisp
```lisp
(defmacro defpipeline (name &body stages)
  `(defparameter ,name
     (list ,@(loop for (stage-name function) in stages
                   collect `(cons ',stage-name #',function)))))

(defpipeline *order-pipeline*
  (:validate    validate-order)
  (:price       calculate-pricing)
  (:check-fraud fraud-check)
  (:charge      process-payment)
  (:fulfill     initiate-fulfillment))

(defun run-pipeline (pipeline input)
  (reduce (lambda (result stage)
            (if (err-p result)
                result
                (funcall (cdr stage) (ok-value result))))
          pipeline
          :initial-value (ok input)))
```

#### Rust
```rust
// Each stage transforms one type into another, with possible failure
fn order_pipeline(input: RawOrder) -> Result<FulfilledOrder, PipelineError> {
    let validated = validate_order(input)?;
    let priced = calculate_pricing(validated)?;
    let checked = fraud_check(priced)?;
    let charged = process_payment(checked)?;
    let fulfilled = initiate_fulfillment(charged)?;
    Ok(fulfilled)
}

// Each intermediate type is distinct and named:
// RawOrder -> ValidatedOrder -> PricedOrder -> CheckedOrder -> ChargedOrder -> FulfilledOrder
// The agent sees the pipeline structure AND the compiler enforces type correctness.
```

#### TypeScript
```typescript
type Stage<I, O> = {
    readonly name: string
    readonly execute: (input: I) => Result<O, PipelineError>
}

// With a pipe utility:
const processOrder = (raw: RawOrder): Result<FulfilledOrder, PipelineError> =>
    pipe(
        validateOrder(raw),
        andThen(calculatePricing),
        andThen(fraudCheck),
        andThen(processPayment),
        andThen(initiateFulfillment),
    )
```

#### Java
```java
public sealed interface PipelineResult<T> permits Success, Failure {
    record Success<T>(T value) implements PipelineResult<T> {}
    record Failure<T>(PipelineError error) implements PipelineResult<T> {}

    default <U> PipelineResult<U> andThen(Function<T, PipelineResult<U>> next) {
        return switch (this) {
            case Success<T> s -> next.apply(s.value());
            case Failure<T> f -> new Failure<>(f.error());
        };
    }
}

// Pipeline reads top to bottom:
PipelineResult<FulfilledOrder> result = PipelineResult.of(rawOrder)
    .andThen(OrderActions::validate)
    .andThen(PricingActions::calculate)
    .andThen(FraudActions::check)
    .andThen(PaymentActions::charge)
    .andThen(FulfillmentActions::initiate);
```

---

### Transform 3: Branching Dispatch -> ADT + Exhaustive Match

**Target:** Replace string/integer dispatch with an enumerated type where the compiler or type checker enforces that every case is handled.

**Before (any language):**
```
if type == "email":    ...
elif type == "sms":    ...
elif type == "push":   ...
# what if someone adds "webhook" and forgets to update this?
```

**After -- the pattern across all five languages:**

#### Python (3.10+)
```python
from enum import Enum, auto
from dataclasses import dataclass

class Notification:
    pass

@dataclass(frozen=True)
class Email(Notification):
    address: str
    subject: str
    body: str

@dataclass(frozen=True)
class Sms(Notification):
    phone: str
    message: str

@dataclass(frozen=True)
class Push(Notification):
    device_id: str
    title: str
    body: str

def send(notification: Notification) -> Result[Sent, SendError]:
    match notification:
        case Email(address, subject, body):
            return send_email(address, subject, body)
        case Sms(phone, message):
            return send_sms(phone, message)
        case Push(device_id, title, body):
            return send_push(device_id, title, body)
```

*Note: Python's match is not exhaustiveness-checked by the language itself. Use a type checker like pyright with `--strict` and ensure no default branch. A `case _:` catch-all defeats the purpose.*

#### Common Lisp
```lisp
(deftype notification ()
  '(or email-notification sms-notification push-notification))

(defstruct (email-notification (:conc-name email-))
  (address "" :type string :read-only t)
  (subject "" :type string :read-only t)
  (body "" :type string :read-only t))

(defstruct (sms-notification (:conc-name sms-))
  (phone "" :type string :read-only t)
  (message "" :type string :read-only t))

(defstruct (push-notification (:conc-name push-))
  (device-id "" :type string :read-only t)
  (title "" :type string :read-only t)
  (body "" :type string :read-only t))

;; Use etypecase for exhaustive dispatch -- signals error on unhandled types
(defun send-notification (notification)
  (etypecase notification
    (email-notification (send-email notification))
    (sms-notification   (send-sms notification))
    (push-notification  (send-push notification))))
```

#### Java
```java
public sealed interface Notification permits Email, Sms, Push {
    record Email(String address, String subject, String body) implements Notification {}
    record Sms(String phone, String message) implements Notification {}
    record Push(String deviceId, String title, String body) implements Notification {}
}

// Exhaustive in switch expressions (Java 21+)
SendResult send(Notification notification) {
    return switch (notification) {
        case Email e -> sendEmail(e.address(), e.subject(), e.body());
        case Sms s -> sendSms(s.phone(), s.message());
        case Push p -> sendPush(p.deviceId(), p.title(), p.body());
    };
}
```

#### Rust
```rust
enum Notification {
    Email { address: String, subject: String, body: String },
    Sms { phone: String, message: String },
    Push { device_id: String, title: String, body: String },
}

fn send(notification: &Notification) -> Result<Sent, SendError> {
    match notification {
        Notification::Email { address, subject, body } => send_email(address, subject, body),
        Notification::Sms { phone, message } => send_sms(phone, message),
        Notification::Push { device_id, title, body } => send_push(device_id, title, body),
    }
}
```

#### TypeScript
```typescript
type Notification =
    | { readonly kind: 'email'; readonly address: string; readonly subject: string; readonly body: string }
    | { readonly kind: 'sms'; readonly phone: string; readonly message: string }
    | { readonly kind: 'push'; readonly deviceId: string; readonly title: string; readonly body: string }

function send(notification: Notification): Result<Sent, SendError> {
    switch (notification.kind) {
        case 'email': return sendEmail(notification.address, notification.subject, notification.body)
        case 'sms': return sendSms(notification.phone, notification.message)
        case 'push': return sendPush(notification.deviceId, notification.title, notification.body)
    }
    // TypeScript knows this is exhaustive -- no default needed.
    // Adding a variant to the union will cause a compile error here.
}
```

---

### Transform 4: Scattered Validation -> Composable Rule Collection

**Target:** All validation rules for a domain concept live in one place, follow the same schema, and compose.

**The universal pattern:**

```
Rule:        named pure predicate with an error message
RuleSet:     collection of rules applied to the same input type
Combinator:  all / any / when(condition, rule) / unless(condition, rule)
Validation:  RuleSet applied to input -> Result[ValidatedInput, list[ValidationError]]
```

#### Python
```python
@dataclass(frozen=True)
class ValidationRule(Generic[T]):
    name: str
    check: Callable[[T], bool]
    error: str

@dataclass(frozen=True)
class ValidationRuleSet(Generic[T]):
    rules: tuple[ValidationRule[T], ...]

    def validate(self, value: T) -> Result[T, list[str]]:
        errors = [rule.error for rule in self.rules if not rule.check(value)]
        return Err(errors) if errors else Ok(value)

order_rules = ValidationRuleSet(rules=(
    ValidationRule("has_items",       lambda o: len(o.items) > 0,           "Order must have items"),
    ValidationRule("valid_total",     lambda o: o.total >= 0,               "Total must be non-negative"),
    ValidationRule("customer_exists", lambda o: o.customer is not None,     "Customer required"),
    ValidationRule("not_duplicate",   lambda o: not is_duplicate(o),        "Duplicate order detected"),
))
```

#### Common Lisp
```lisp
(defmacro defruleset (name type &body rules)
  `(defparameter ,name
     (list ,@(loop for (rule-name check error) in rules
                   collect `(list ',rule-name ,check ,error)))))

(defruleset *order-rules* order
  (:has-items       (lambda (o) (> (length (order-items o)) 0))    "Order must have items")
  (:valid-total     (lambda (o) (>= (order-total o) 0))           "Total must be non-negative")
  (:customer-exists (lambda (o) (not (null (order-customer o))))   "Customer required")
  (:not-duplicate   (lambda (o) (not (duplicate-order-p o)))       "Duplicate order detected"))

(defun validate (ruleset value)
  (let ((errors (loop for (name check error) in ruleset
                      unless (funcall check value)
                      collect (cons name error))))
    (if errors
        (err errors)
        (ok value))))
```

#### TypeScript
```typescript
type ValidationRule<T> = {
    readonly name: string
    readonly check: (value: T) => boolean
    readonly error: string
}

const orderRules: readonly ValidationRule<Order>[] = [
    { name: 'has_items',       check: o => o.items.length > 0,     error: 'Order must have items' },
    { name: 'valid_total',     check: o => o.total >= 0,           error: 'Total must be non-negative' },
    { name: 'customer_exists', check: o => o.customer != null,     error: 'Customer required' },
    { name: 'not_duplicate',   check: o => !isDuplicate(o),        error: 'Duplicate order detected' },
] as const

const validate = <T>(rules: readonly ValidationRule<T>[], value: T): Result<T, string[]> => {
    const errors = rules.filter(r => !r.check(value)).map(r => r.error)
    return errors.length > 0 ? err(errors) : ok(value)
}
```

---

### Transform 5: Exception Control Flow -> Result/Either Types

**Target:** Functions that can fail return a Result type. The caller handles both paths explicitly. No invisible control flow.

**The universal pattern:**

```
Result<T, E> = Ok(T) | Err(E)

Functions return Result instead of throwing.
Callers use match/andThen/map instead of try/catch.
Exceptions are reserved for truly unexpected failures (bugs, OOM, hardware).
```

**Language-specific Result types:**

- **Python:** Use the `result` library, or define your own with dataclasses
- **Common Lisp:** Define `ok`/`err` structs, or use the condition system declaratively (conditions + restarts are already more explicit than exceptions)
- **Java:** `sealed interface Result<T, E> permits Ok, Err` with `andThen` method
- **Rust:** Built-in `Result<T, E>` with `?` operator -- already the idiomatic pattern
- **TypeScript:** Define `type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }` or use libraries like `neverthrow`, `fp-ts`

---

### Transform 6: Mutable Data -> Immutable Data with Transformation Functions

**Target:** Data structures are created once and never modified. "Updates" produce new instances. Deeply nested updates use copy-with-override patterns or optics.

#### Python
```python
@dataclass(frozen=True)
class Order:
    id: str
    items: tuple[Item, ...]  # tuple, not list
    status: OrderStatus
    total: Decimal

# "Update" by creating a new instance:
def apply_discount(order: Order, discount: Decimal) -> Order:
    return dataclasses.replace(order, total=order.total * (1 - discount))
```

#### Common Lisp
```lisp
;; Use :read-only slots
(defstruct (order (:conc-name order-))
  (id "" :type string :read-only t)
  (items '() :type list :read-only t)
  (status :pending :type keyword :read-only t)
  (total 0 :type number :read-only t))

;; "Update" by copying with changes
(defun apply-discount (order discount)
  (let ((new-total (* (order-total order) (- 1 discount))))
    (make-order :id (order-id order)
                :items (order-items order)
                :status (order-status order)
                :total new-total)))

;; Or define a generic copy-with utility
(defmacro copy-struct (struct type &rest overrides)
  ;; generates a make-TYPE call copying all slots, overriding specified ones
  ...)
```

#### Rust
```rust
#[derive(Debug, Clone)]
struct Order {
    id: String,
    items: Vec<Item>,  // owned, not shared mutably
    status: OrderStatus,
    total: Decimal,
}

fn apply_discount(order: Order, discount: Decimal) -> Order {
    Order {
        total: order.total * (Decimal::ONE - discount),
        ..order
    }
}
```

#### TypeScript
```typescript
type Order = {
    readonly id: string
    readonly items: readonly Item[]
    readonly status: OrderStatus
    readonly total: number
}

const applyDiscount = (order: Order, discount: number): Order => ({
    ...order,
    total: order.total * (1 - discount),
})
```

#### Java
```java
// Records are immutable by default
public record Order(String id, List<Item> items, OrderStatus status, BigDecimal total) {
    // Canonical constructor can enforce immutability of the list
    public Order {
        items = List.copyOf(items);
    }

    public Order withTotal(BigDecimal newTotal) {
        return new Order(id, items, status, newTotal);
    }

    public Order applyDiscount(BigDecimal discount) {
        return withTotal(total.multiply(BigDecimal.ONE.subtract(discount)));
    }
}
```

---

### Transform 7: Business Rules as Data (DSL Configuration)

**Target:** When a system has many rules of the same *kind* (pricing rules, routing rules, permission rules, notification rules), express them as a regular data structure -- a table -- rather than scattered conditionals.

**This is the highest-leverage DSL pattern.** It is the direct expression of "logic as configuration."

#### Python
```python
@dataclass(frozen=True)
class PricingRule:
    name: str
    applies_when: Callable[[Order], bool]
    compute: Callable[[Order, Decimal], Decimal]
    priority: int = 0

pricing_rules: tuple[PricingRule, ...] = (
    PricingRule(
        name="bulk_discount",
        applies_when=lambda o: len(o.items) > 10,
        compute=lambda o, total: total * Decimal("0.9"),
        priority=10,
    ),
    PricingRule(
        name="loyalty_discount",
        applies_when=lambda o: o.customer.loyalty_tier > 2,
        compute=lambda o, total: total * Decimal("0.95"),
        priority=20,
    ),
    PricingRule(
        name="holiday_surcharge",
        applies_when=lambda o: is_holiday(o.date),
        compute=lambda o, total: total + Decimal("5.00"),
        priority=5,
    ),
)

def apply_pricing(order: Order, rules: tuple[PricingRule, ...]) -> Decimal:
    applicable = sorted(
        [r for r in rules if r.applies_when(order)],
        key=lambda r: r.priority,
    )
    return reduce(lambda total, rule: rule.compute(order, total), applicable, order.base_total)
```

An agent asked to "add a first-time customer discount" writes one `PricingRule` entry. It does not touch `apply_pricing`. It does not read any control flow. It follows the schema.

---

## Anti-Patterns: FP and DSL Patterns That Hurt Agent-Amenability

### Avoid: Point-Free / Tacit Style

```python
# Bad: agent cannot easily read or modify this
process = compose(
    partial(filter, both(propgt('age', 18), propeq('active', True))),
    partial(sort_by, prop('name')),
    partial(map, pick(['id', 'name'])),
)

# Good: explicit, named, each step is readable
def process(users: list[User]) -> list[UserSummary]:
    return pipe(
        users,
        lambda us: [u for u in us if u.age > 18 and u.active],
        lambda us: sorted(us, key=lambda u: u.name),
        lambda us: [UserSummary(id=u.id, name=u.name) for u in us],
    )

# Better: named stages
def active_adults(users: list[User]) -> list[User]:
    return [u for u in users if u.age > 18 and u.active]

def by_name(users: list[User]) -> list[User]:
    return sorted(users, key=lambda u: u.name)

def summarize(users: list[User]) -> list[UserSummary]:
    return [UserSummary(id=u.id, name=u.name) for u in users]

process = pipeline(active_adults, by_name, summarize)
```

### Avoid: Deep Monad Transformer Stacks

```typescript
// Bad: agent must understand the monad stack to make any change
const program: ReaderTaskEither<AppConfig, AppError, Result> = pipe(
    RTE.ask<AppConfig>(),
    RTE.chainW(config => pipe(
        TE.tryCatch(() => fetchUser(config.db), toAppError),
        TE.chainW(user => TE.tryCatch(() => validate(user), toAppError)),
    )),
)

// Good: explicit dependency passing, Result type at each step
const processUser = (config: AppConfig): Result<ProcessedUser, AppError> =>
    pipe(
        fetchUser(config.db),
        andThen(validateUser),
        andThen(enrichUser(config.featureFlags)),
        andThen(persistUser(config.db)),
    )
```

### Avoid: Opaque Macros (Common Lisp)

```lisp
;; Bad: agent cannot see what this expands to or how to modify it
(with-transactional-workflow (:retry 3 :on-error :rollback)
  (validate-and-process order)
  (charge-and-fulfill order))

;; Good: the workflow is data, the execution strategy is explicit
(run-workflow *order-workflow* order
  :error-policy (retry-policy :max-attempts 3 :on-exhaustion :rollback))
```

### Avoid: Excessively Generic Type-Level Programming

```rust
// Bad: agent cannot understand what concrete thing this does
fn process<T, E, F, G>(input: T, f: F, g: G) -> Result<G::Output, E>
where
    F: Fn(T) -> Result<F::Output, E>,
    G: Fn(F::Output) -> Result<G::Output, E>,
    F: Transform<T>,
    G: Transform<F::Output>,
{ ... }

// Good: concrete types, named stages
fn process_order(input: RawOrder) -> Result<FulfilledOrder, OrderError> {
    let validated = validate(input)?;
    let priced = price(validated)?;
    let fulfilled = fulfill(priced)?;
    Ok(fulfilled)
}
```

### The Rule of Thumb

**If an agent needs to understand an abstraction mechanism before it can understand the domain logic, the abstraction is hurting, not helping.** The domain logic should be immediately legible. The plumbing that executes it can be sophisticated, but the *definition* of what the system does must be readable as a description of the domain.

---

## Decision Heuristics: When NOT to Transform

**Do not transform when:**

1. **The code is simple and linear.** A 10-line function that reads clearly as imperative code does not need to become a pipeline. The overhead of the abstraction exceeds its value.

2. **Performance is critical and measured.** Inner loops, hot paths, real-time systems. Immutable data structures with copying have real costs. Profile first, then decide.

3. **The code is a leaf node with no workflow character.** A utility function that parses a date string is fine as a simple function. Not everything is a workflow or a rule set.

4. **The team or codebase has strong existing conventions.** If you are making a targeted change to a large OOP Java codebase, introducing ADTs in one file creates inconsistency that may hurt more than it helps. Consider the scope of transformation.

5. **The domain genuinely has no regularity.** If there are only two cases and they are genuinely different in kind, a match on an ADT buys you little over an if/else. The pattern shines when there are N cases and N will grow.

**Always transform when:**

1. **There is a state machine.** Always. No exceptions. State machines expressed imperatively are the worst case for agent modification.

2. **There are more than three cases of the same kind of thing.** Three pricing rules, three notification types, three validation checks -- the moment there are several instances of a pattern, tabularize them.

3. **The code will be modified by agents repeatedly.** If this is a one-time script, don't bother. If it's a living system that agents will evolve, the investment in declarative structure pays off immediately.

4. **Side effects are interleaved with logic.** Separate them. Always.

---

## Applying the Skill: Sequence of Operations

When invoked on a codebase:

1. **Inventory the codebase for diagnostic patterns.** Scan for the six diagnostic patterns. Rank by severity.

2. **Start with state machines.** Transform 1 gives the highest return. Identify every implicit state machine and convert it to a transition table.

3. **Then separate side effects from logic.** In every workflow, identify where I/O, logging, and notifications happen. Move them to effect declarations.

4. **Then convert branching dispatch to ADTs.** Every string/integer dispatch becomes a typed enum with exhaustive matching.

5. **Then tabularize repeated rules.** Pricing, validation, routing, permissions -- anything with multiple instances of the same pattern becomes a rule table.

6. **Then convert imperative sequences to typed pipelines.** Long functions become named stages with typed inputs and outputs.

7. **Then make data immutable.** Replace mutable classes/structs with frozen/readonly equivalents. Replace mutation with copy-on-write.

8. **Finally, introduce Result types for error handling.** Replace exception-based control flow with explicit Result returns.

This ordering is deliberate: each step makes the subsequent steps easier, and the early steps deliver the most value for agent-amenability.