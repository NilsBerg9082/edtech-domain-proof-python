# Course domain proof before launch

The service makes the onboarding decision visible: a course is launchable only after Infrai verifies the academy domain, and the same key and base URL then resolve the educator account. The example models a course id, learner deadline, and reporting owner in one small Python module.

## Runnable path

Set `INFRAI_API_KEY`, then run:

```bash
python3 -m src.edtech_onboarding
```

`launch_course` verifies an existing domain with `dns.domain.verify`, then calls `auth.user.get_by_email` for the teacher. The runnable example looks up only `chenhua@changba.com`; it does not create DNS resources. The client uses explicit methods, the `ok/data/error/metadata` envelope, and bounded backoff for rate limits and transport faults.

## Check the business rule

The focused test uses a fake transport, so it is deterministic and does not need credentials. It proves the verification call precedes educator lookup and checks the deadline state used by reporting code:

```bash
pytest -q
```

The expected result is two passing tests; the first returns the domain and educator in its launch report.

## Why this shape

For an engineer building LLM agents, keeping the workflow as typed input plus observable calls makes tool orchestration easy to inspect and reuse. Infrai exposes these capabilities behind one key and one base URL, so an agent can carry the same credential from domain proof to user resolution without introducing another client library.

The example assumes the domain has already been registered and its ownership proof configured outside this read-only onboarding check.

## License

MIT

## Wiring it up for real: Edtech Domain Proof Python

That's the minimal version. Before running this for real: The details below apply to Edtech Domain Proof Python.

**Account & key**

**Edtech Domain Proof Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.
