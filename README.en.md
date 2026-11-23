# MotorCare

[中文](README.md) | **English**

**A multimodal AI prototype for industrial motor after-sales troubleshooting.**

MotorCare combines fault descriptions, alarm images, and maintenance knowledge to help after-sales engineers and maintenance personnel organize evidence, identify next checks, and prepare service records for handover. Users can add site observations and inspection results through follow-up messages to refine the analysis.

Built with Python, Gradio, and the MiMo API, this is a course project for **IS5542 Generative AI for Business**, intended primarily for local demonstration.

## Supported scope

| Item | Current support |
| --- | --- |
| Motor | BLM230-A2 |
| Driver | BMUD30-C2 |
| Alarms | AL46, AL30, AL28 |
| Languages | Chinese and English |

The knowledge base covers this equipment combination and alarm scope. Results support troubleshooting and require review by a qualified engineer.

## Features

- Chinese and English interfaces and responses; up to 3 images per ticket and 12 conversation turns.
- Troubleshooting and service record tabs; generate, update, and copy records.
- Linked motor/driver selection; currently only the equipment combination above is supported.
- Server-side scope instructions, screening for obvious out-of-scope or instruction-override requests, and API rate and usage limits.

## Workflow

1. Select the motor, compatible driver, and interface language.
2. Describe the fault and optionally upload alarm or site images.
3. Review the AI analysis, suggested checks, and requests for missing information.
4. Add inspection results and continue the conversation.
5. Generate a service record, review it, and copy it for handover.

The Python backend sends the user input, conversation context, and compact knowledge base to the MiMo model, then displays the response through Gradio. Images and fault descriptions are sent to the configured external API; use only material you are authorized to provide.

## Quick start

Requirements: **Python 3.12**, Git, and access to a **MiMo API model that supports image input**. Model requests require internet access and may incur API charges.

```bash
git clone https://github.com/RyougiShiya/IS5542-MotorCare-after-sales-workplace.git
cd IS5542-MotorCare-after-sales-workplace
```

```bash
conda create -n motorcare python=3.12 -y
conda activate motorcare
```

From the project directory containing `app.py`:

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

In Windows Command Prompt, use `copy .env.example .env` instead.

Edit your local `.env` file:

```dotenv
MIMO_BASE_URL=your_mimo_api_base_url
MIMO_API_KEY=your_api_key
MIMO_MODEL=mimo-v2.6-flash
```

Replace the placeholders before running. The model must support image input; use the endpoint and model available to your account. **Never commit your .env file.**

```bash
python app.py
```

Open the local URL printed in the terminal, using the actual port shown. The app listens on localhost by default and does not generate a public link.

## Switching models through `.env`

This project uses **MiMo by default**, with `mimo-v2.6-flash` as the example model. To use another model or provider, you can change only the project-root `.env` file **without editing Python code**, provided the target API supports the request format described below.

### Configuration steps

1. Stop the running app by pressing `Ctrl+C` in its terminal.
2. Replace the values of these three settings in `.env`:

```dotenv
MIMO_BASE_URL=https://your-provider.example/v1
MIMO_API_KEY=your_provider_api_key
MIMO_MODEL=your_vision_model_id
```

| Setting | Value |
| --- | --- |
| `MIMO_BASE_URL` | The provider's documented OpenAI-compatible API base URL; do not use a web chat URL or append `/chat/completions` yourself |
| `MIMO_API_KEY` | Your API key for that provider |
| `MIMO_MODEL` | A model ID supported by that endpoint and available to your account |

The URL and credentials above are placeholders. **Keep the `MIMO_` variable names unchanged and replace only their values.** These are the names read by the application; the prefix does not require using MiMo as the provider. Preserve other settings in `.env`. No changes to the knowledge base or interface code are required.

3. Save the file and restart the app:

```bash
python app.py
```

Refreshing the browser alone does not reload configuration. If variables with the same names are already set in the launch environment, update or remove them as well: the current `.env` loader does not override existing environment variables.

### API compatibility requirements

Switching through `.env` alone requires support for the complete request currently sent by the application:

- An OpenAI-compatible **Chat Completions** endpoint and `system` messages.
- Multimodal `image_url` inputs, including inline image data URLs.
- JSON output mode through `response_format={"type":"json_object"}`.
- The `max_completion_tokens` parameter.
- The `thinking={"type":"disabled"}` parameter, or the ability to safely ignore that field.

**OpenAI compatibility does not guarantee compatibility with every parameter.** Providers that reject these fields, expose a different API format, or offer text-only models may require request-code changes. Other providers have not been individually verified.

After switching, check a text-only case, an image case, follow-up messages, Chinese and English responses, and service record generation. A successful connection does not establish equivalent diagnostic quality. Pricing and data handling policies may also differ between providers. Never commit a `.env` file containing real credentials.

## Example cases

Press **Alt/Option + Shift + D** to show or hide the example panel, or **Esc** to close it. Drag its title bar to reposition it.

1. Open the demonstration panel, select a case, and send it.
2. After receiving a response, select the follow-up information button and send the additional information to see the analysis updated.
3. Generate the service record and review it. Update the record after adding further information.
4. Confirm clearing the current ticket before switching away from a ticket that contains information.

This repository includes a self-created **simulated alarm illustration for AL46**. **AL30 and AL28 are text-only cases.** Original manufacturer images, product photographs, and complete PDF manuals are not included. You may upload site photographs you have permission to use. This simulated demonstration does not establish recognition accuracy on real photographs.

## Structure and maintenance

- `app.py`: application entry point.
- `motorcare/`: model integration, interface, path handling, and safeguards; `assets/` contains CSS and JavaScript.
- `data/knowledge_base/`: bilingual knowledge in `chunks.json`, sources in `sources.json`, and rules in `answer_policy.json`.
- `data/cases/`: `cases.json` defines the demonstration cases; `images/` stores case images. Image paths are relative to `data/cases/`.
- `scripts/`: offline checks.

When adding knowledge, register its source and a unique identifier, and keep Chinese and English coverage aligned. Supporting another alarm also requires updating the supported scope in `engine.py`, `answer_policy.json`, `cases.json`, and the bilingual case button order in `ui.py`, followed by model regression checks.

The entire compact knowledge base is included in the prompt. **The app does not use a vector database or retrieval-based RAG.**

## Offline checks

```bash
python scripts/check_project.py
python scripts/check_workspace.py
python scripts/check_security.py
```

These checks do not call the model and do not replace testing with the live API and a browser.

## Configuration and limitations

By default, the application permits **6 model calls per minute** and **60 calls per rolling 24 hours**, including service record generation and failed requests. Configure these limits through `MOTORCARE_CALLS_PER_MINUTE` and `MOTORCARE_CALLS_PER_24H` in `.env`.

Usage counters are stored in `var/usage.sqlite3`, which contains neither tickets nor API keys. Counters survive a restart on the same disk but are lost if the disk is cleared or an ephemeral container is rebuilt. These safeguards are intended for a single application instance and are not an account-level spending cap.

The default host is `MOTORCARE_HOST=127.0.0.1`. Binding to a public interface requires `MOTORCARE_USERNAME` and a `MOTORCARE_PASSWORD` of at least 12 characters. Public deployment also requires HTTPS and access-control verification. Prompt instructions and heuristic screening cannot guarantee protection against all prompt injection attacks. Do not expose the local app through an unauthenticated tunnel.

Tickets are kept only within the session; this is not a persistent ticket management system. **Word/PDF export is not implemented; copying is supported.** This project is not an official manufacturer product and does not guarantee diagnosis or repair outcomes.

## Sources and licensing

Maintenance references are listed in [sources.json](data/knowledge_base/sources.json). Manufacturer materials and trademarks remain the property of their respective owners.

This repository does not currently include an open-source license. Public availability does not grant permission to copy, modify, or redistribute the project; contact the project authors to clarify permission before reuse.
